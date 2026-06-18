# sources/distributed-fs/ceph/src/rgw/rgw_tag.cc

## Purpose
`rgw_tag.cc` implements RGW object tag storage and parsing helpers.

## Important APIs, Types, and Functions
`add_tag()` and `emplace_tag()` insert into the multimap. `check_and_add_tag()` enforces count, key length, value length, and non-empty key limits. `set_from_string()` parses URL-encoded `k=v&k2=v2` tag strings. `dump()` emits a `tagset` object. `generate_test_instances()` supplies encode-test fixtures.

## Control Flow
Input strings are split on `&`; each component is split on the first `=`, URL-decoded, validated, and inserted. The function returns immediately on invalid tag input.

## State and Persistence Behavior
Tags are held in an in-memory multimap and encoded by the header. No external persistence is performed here.

## Dependencies and Integration Points
Depends on `rgw_tag.h`, `rgw_common.h` URL decoding, Boost string split, Formatter, and RGW error codes. Used by S3 tagging, sync filters, lifecycle, and metadata paths.

## Risks
The max tag count check runs before insert, so duplicate multimap keys count independently. URL decoding errors are not surfaced separately. Empty values are allowed by core tags but S3 XML layer rejects empty values.

## Test Signals
Cover empty input, URL-encoded keys/values, missing `=`, duplicate keys, max count, maximum key/value lengths, empty keys, and formatter output.
