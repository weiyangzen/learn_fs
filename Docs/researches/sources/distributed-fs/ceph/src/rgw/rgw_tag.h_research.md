# sources/distributed-fs/ceph/src/rgw/rgw_tag.h

## Purpose
`rgw_tag.h` declares `RGWObjTags`, the versioned RGW object-tag container.

## Important APIs, Types, and Functions
`RGWObjTags` stores tags as `std::multimap<std::string,std::string>`, exposes add/validate/parse/clear/count/access methods, and provides Ceph encode/decode, Formatter dump, and test instances. The decode path first tries binary Ceph format, then falls back to legacy URL-encoded plain text.

## Control Flow
Decoding saves the starting iterator, attempts `DECODE_START_LEGACY_COMPAT_LEN`, and on `buffer::error` restores the iterator, copies remaining bytes, strips trailing nulls, and calls `set_from_string()`.

## State and Persistence Behavior
This is a durable object metadata format. Struct version 1 encodes the tag multimap. Legacy plain-string fallback preserves older object tag values.

## Dependencies and Integration Points
The header depends on Ceph encoding and Formatter forward declarations. It is used by S3 tagging, sync policy tag filters, and object metadata encoding.

## Risks
Fallback decoding can reinterpret arbitrary invalid binary bytes as a tag string if they parse. Multimap semantics allow duplicate keys. Limits are instance-level for tag count but compile-time for key/value lengths.

## Test Signals
Binary and legacy string decode tests, trailing null stripping, invalid fallback rethrow behavior, duplicate tag encode/decode, and custom max tag count coverage are important.
