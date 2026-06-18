# sources/distributed-fs/ceph/src/rgw/rgw_xml.h

## Purpose
`rgw_xml.h` declares RGW's XML object tree, parser, generic decode templates, and XML encoder overloads.

## Important APIs, Types, and Functions
`XMLObjIter`, `XMLObj`, and `RGWXMLParser` form the parse tree API. `RGWXMLDecoder::err` is the exception type for decode failures. Template `decode_xml()` overloads decode one object, vectors, callback-driven containers, and defaulted values. Free `decode_xml_obj()` overloads supply type-specific conversion. Template `encode_xml()` and `do_encode_xml()` emit object, namespace, vector/list, and optional XML structures.

## Control Flow
Callers parse XML into an `RGWXMLParser`, then call `RGWXMLDecoder::decode_xml()` on named children. Missing mandatory fields throw. Decode errors are wrapped with the field name. Encoder helpers open Formatter sections and call `dump_xml()` on complex values.

## State and Persistence Behavior
The header defines transient parsing and formatting contracts, not persistent storage. It is used to translate request XML into persisted RGW structs.

## Dependencies and Integration Points
Depends on Ceph buffer forwards, Formatter, Ceph time, XML Expat forward declarations, and STL containers. Integrated into many RGW REST resource parsers.

## Risks
Template decode resets missing optional values to default-constructed `T`, which can erase prior caller state. `XMLObjIter` typedefs const and non-const iterators to the same mutable iterator type. Complex type support relies on ADL/free `decode_xml_obj()` overloads.

## Test Signals
Cover template behavior for scalar, vector, list callback, optional, defaulted decode, mandatory missing fields, error wrapping, and encoder section nesting.
