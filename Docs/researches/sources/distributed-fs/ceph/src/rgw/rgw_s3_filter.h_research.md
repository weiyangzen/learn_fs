# sources/distributed-fs/ceph/src/rgw/rgw_s3_filter.h

## Purpose
`rgw_s3_filter.h` declares serializable filter structures for S3 bucket notifications. It is the contract used to store, decode, dump, and evaluate key, metadata, and tag filters.

## Important APIs, Types, and Functions
`rgw_s3_key_filter` stores `prefix_rule`, `suffix_rule`, and `regex_rule`, with content checks, XML/JSON formatting, XML decode, and Ceph encoding. `rgw_s3_key_value_filter` stores a `boost::container::flat_map<std::string,std::string>` for metadata or tag filter rules. `rgw_s3_filter` composes key, metadata, and tag filters. Free `match()` overloads evaluate key filters, flat metadata maps, multimap tags, and complete object filters.

## Control Flow
Configuration decode fills the structs from XML. Persistence uses the inline encode/decode methods. Runtime notification code calls the appropriate `match()` overload, usually the object-level matcher, against a SAL object with cached attrs.

## State and Persistence Behavior
The key and key-value filters are version 1 encodings. The composite `rgw_s3_filter` is version 2 with backwards-compatible decoding that only reads `tag_filter` for version 2 or newer payloads. No runtime state is stored beyond filter fields.

## Dependencies and Integration Points
The header depends on Ceph `bufferlist` encoding, `Formatter`, `XMLObj`, `boost::container::flat_map`, and SAL object types. It is included by notification and pubsub configuration code.

## Risks
Filter structures expose public fields, so validation is concentrated in XML decode and can be bypassed by internal callers. Runtime regex validity is not represented in the type. The complete-object matcher returns a boolean without explaining which category matched, limiting diagnostics.

## Test Signals
Tests should verify encoder compatibility, XML round trips, `has_content()` for each filter type, public-field direct construction behavior, and object-level matching with empty filters and null object pointers.
