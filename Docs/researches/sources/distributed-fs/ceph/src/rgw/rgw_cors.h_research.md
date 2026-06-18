# sources/distributed-fs/ceph/src/rgw/rgw_cors.h

## Purpose
Declares the common CORS data model, method bit flags, validation helpers, and serialization contract used by RGW bucket CORS configuration.

## Important APIs, types, and functions
`RGWCORSRule` owns max age, allowed method flags, optional id, allowed headers, allowed origins, and exposed headers. It exposes rule construction, matching, formatting, dumping, and encode/decode. `RGWCORSConfiguration` owns a list of rules and provides lookup, origin-list extraction, deletion, dumping, and `stack_rule()` insertion. `validate_name_string()` rejects empty names and names with more than one wildcard. `get_cors_method_flags()` maps one method string, while `get_multi_cors_method_flags()` parses a delimited list.

## Control flow
Callers parse protocol-specific configuration into `RGWCORSRule` instances, push them into `RGWCORSConfiguration`, persist the config as encoded attrs, then consult the list during preflight and actual request handling.

## State and persistence
The header defines versioned `ENCODE_START`/`DECODE_START` layouts for both rule and configuration, making this file part of the bucket metadata compatibility surface.

## Dependencies and integration points
Depends on Ceph `bufferlist` encoding, `include/types.h`, string-list splitting, and protocol adapters such as `rgw_cors_s3.*` and `rgw_cors_swift.h`.

## Risks and test signals
Because method flags are `uint8_t`, future methods must fit the bitset. Tests should validate method parsing delimiters, unsupported method behavior, encode compatibility, wildcard validation, and mutable-header-cache behavior noted by the class comment.
