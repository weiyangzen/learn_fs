# sources/distributed-fs/ceph/src/rgw/rgw_xml.cc

## Purpose
`rgw_xml.cc` implements RGW's lightweight Expat-backed XML tree, decoder primitives, and XML encoder overloads.

## Important APIs, Types, and Functions
`XMLObjIter` iterates child maps. `XMLObj` stores tag type, text data, children, attributes, and callbacks for parser events. `RGWXMLParser` owns an Expat parser, buffers input, creates allocated or lazy XML objects, and exposes `init()`/`parse()`. `decode_xml_obj()` overloads parse numeric types, bool, base64 bufferlist, `utime_t`, and `real_time`. `encode_xml()` overloads dump strings, bool, integers, times, and base64 bufferlists.

## Control Flow
`RGWXMLParser::init()` registers static callbacks. `parse()` appends incoming bytes to its saved buffer and calls Expat. Start callbacks allocate an object, link it to the current object, and push it on a stack vector. End callbacks invoke `xml_end()` and restore the parent. Character callbacks append data to the current object. Higher-level decode templates in the header traverse this tree.

## State and Persistence Behavior
The XML tree and parse buffer are in-memory request state. No durable persistence occurs here, but many RGW metadata XML APIs rely on these conversions before persisting decoded structs.

## Dependencies and Integration Points
Depends on Expat, Ceph bufferlist, Formatter, `utime_t`, and RGW XML declarations. Used broadly by S3/Swift XML REST APIs such as tagging, website config, ACLs, lifecycle, and notifications.

## Risks
`call_xml_handle_data()` assumes `cur_obj` is non-null. `parse()` retains a full copy of all parsed input, which can be expensive for large XML bodies. Parse errors are printed to stderr. Numeric decoders accept trailing whitespace but reject other suffixes. `strncasecmp(..., 8)` treats strings beginning with `true` or `false` as booleans even with suffixes inside 8-byte comparison behavior.

## Test Signals
Cover incremental parse, attributes, repeated child tags, mandatory and optional decode, numeric range errors, bool parsing, base64 decode failure, time parsing, custom `alloc_obj()` ownership, parse failure, and encoder output.
