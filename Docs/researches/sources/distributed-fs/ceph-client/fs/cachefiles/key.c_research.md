# sources/distributed-fs/ceph-client/fs/cachefiles/key.c

## Purpose
`key.c` converts FS-Cache binary cookie keys into safe CacheFiles backing filenames.

## Important APIs, Types, and Functions
The primary API is `cachefiles_cook_key`. Helpers and data tables include `cachefiles_charmap`, `cachefiles_filecharmap`, and `how_many_hex_digits`.

## Control Flow
The function reads the cookie key, rejects keys that exceed the NAME_MAX-derived limit via `BUG_ON`, then chooses one of three encodings. Printable filename-safe ASCII keys are prefixed with `D` and copied directly. Non-printable keys are compared against compact big-endian and little-endian 32-bit hex chunk encodings, prefixed `S` or `T`, and the shorter one is used when it beats base64 length. Otherwise a custom base64-like encoding prefixed `E` plus padding count maps 3 raw bytes to 4 safe characters.

## State and Persistence Behavior
The computed name is allocated and stored in `object->d_name`. It becomes part of the persistent backing path `cache/volume/fanout/name`, so encoding stability is required for cache reuse across mounts and daemon restarts.

## Dependencies and Integration Points
It depends on FS-Cache cookie keys (`fscache_get_key`, `key_len`) and is called by `cachefiles_lookup_cookie` before namei lookup or creation.

## Risks and Edge Cases
Filename encoding is an on-disk ABI. Any change to prefixes, charmap, endian choice, padding, or printable-character policy can orphan existing cache entries. The code assumes padded key memory for 32-bit chunk reads. Slash, space, tab, and control characters must never appear directly in filenames.

## Test Signals
Test printable keys, slash/control/non-ASCII keys, short and non-multiple-of-three keys, all-zero and endian-sensitive 32-bit chunks, maximum-length keys, and stable encoded output across architectures.
