#!/usr/bin/python
#_*_ coding:UTF-8 _*_
# 
# Copyright by wshen324. All Rights Reserved.

import urllib2
from sgmllib import SGMLParser
from xml.etree.ElementTree import Element, SubElement, tostring

MVNREPOSITORY_URL = 'http://mvnrepository.com'

class PageParser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.results = []
        self.find_im = False
        self.find_title = False
        self.find_subtitle = False
        self.find_group = False
        self.find_artifact = False
    def check_attr(self, attrs, name, value):
        attr_value = self.get_attr(attrs, name);
        return value == attr_value
    def get_attr(self, attrs, name):
        for attr in attrs:
            if name == attr[0]:
                return attr[1]
        return None
    def has_item(self, name):
        return self.item.has_key(name)
    def start_div(self, attrs):
        if self.check_attr(attrs, 'class', 'im'):
            self.find_im = True
            self.item = {}
    def start_a(self, attrs):
        if self.find_im:
            if not self.has_item('link'):
                self.item['link'] = "%s%s" % (MVNREPOSITORY_URL, self.get_attr(attrs, 'href'))
            elif not self.has_item('title'):
                self.find_title = True
            elif self.find_subtitle:
                if not self.has_item('group'):
                    self.find_group = True
                elif not self.has_item('artifact'):
                    self.find_artifact = True
    def start_p(self, attrs):
        if self.find_im:
            if self.check_attr(attrs, 'class', 'im-subtitle'):
                self.find_subtitle = True
    def handle_data(self, data):
        if self.find_im:
            if self.find_title:
                self.item['title'] = data
                self.find_title = False
            elif self.find_subtitle and self.find_group:
                self.item['group'] = data
                self.find_group = False
            elif self.find_subtitle and self.find_artifact:
                self.item['artifact'] = data
                self.results.append(self.item)
                self.item = {}
                self.find_im = False
                self.find_title = False
                self.find_subtitle = False
                self.find_group = False
                self.find_artifact = False

def parse(query):
    response = urllib2.urlopen("%s/search?q=%s" % (MVNREPOSITORY_URL, query))
    page = response.read()
    parser = PageParser()
    parser.feed(page);
    return parser.results

def wrapper_item(item, query):
    attr = {
        'uid': '1'
        ,'arg': item['link']
    }
    element = Element(u'item', attr)
    SubElement(element, u'title').text = unicode(item['title'])
    SubElement(element, u'subtitle').text = unicode("%s >> %s" % (item['group'], item['artifact']))
    SubElement(element, u'icon', {'type': 'png'}).text = unicode('icon.png')
    return element

def wrapper(items, query):
    root = Element('items')
    for item in items:
        root.append(wrapper_item(item, query))
    return tostring(root, encoding='utf-8')

def search(query):
    items = parse(query)
    text = wrapper(items, query)
    fileHandler = open('/tmp/alfred.log', 'w')
    fileHandler.write(text)
    fileHandler.close()
    return text

if __name__ == "__main__":
    search('spring-boot')
