# sources/distributed-fs/ceph/src/rgw/rgw_placement_types.h

## Purpose
`rgw_placement_types.h` defines `rgw_placement_rule`, the serialized representation of a placement target name plus storage class used by RGW buckets and object placement decisions.

## Important APIs, Types, And Functions
`rgw_placement_rule` stores `name` and `storage_class`, provides constructors, `empty()`, `inherit_from()`, `clear()`, `init()`, canonical storage-class helpers, comparison/equality, encoder/decoder, JSON dump, test instances, `to_str()`, `to_str_explicit()`, `from_str()`, and `standard_storage_class()`. `RGW_STORAGE_CLASS_STANDARD` is the default canonical class.

## Control Flow
Serialization encodes a single string for backward compatibility rather than an encoded struct envelope. `to_str()` omits `/STANDARD` for standard storage class, while `to_str_explicit()` always includes a slash. `from_str()` splits on the first slash and treats no slash as standard class.

## State And Persistence
Placement rules are persisted in bucket/zone placement metadata through their string encoding. Empty `storage_class` and explicit `STANDARD` compare equivalent through `get_storage_class()`.

## Dependencies And Integration Points
The type is used by bucket creation, metadata update, copy/storage-class checks, zone placement config, and data placement targets. It depends only on core types, buffer encoding, and formatter support.

## Risks And Test Signals
Risks include slash handling in placement names, the non-const global string definition in a header, compatibility of string-only encoding, and standard-class equivalence. Tests should cover encode/decode, `STANDARD` versus empty equality, non-standard storage classes, inherited placement, and sorting/compare semantics.
