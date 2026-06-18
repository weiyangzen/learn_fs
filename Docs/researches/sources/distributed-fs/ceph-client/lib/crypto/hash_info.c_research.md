# sources/distributed-fs/ceph-client/lib/crypto/hash_info.c

## Purpose
Defines exported metadata tables mapping kernel `enum hash_algo` values to algorithm names and digest sizes.

## Important APIs, Types, and Functions
- Exports `hash_algo_name[HASH_ALGO__LAST]`.
- Exports `hash_digest_size[HASH_ALGO__LAST]`.
- Covers MD4, MD5, SHA-1, RIPEMD variants, SHA-2, Whirlpool, Tiger, SM3, Streebog, and SHA-3 variants as defined in `<crypto/hash_info.h>`.

## Control Flow and State
There is no runtime control flow. The file initializes two const arrays indexed by enum values. State is static read-only data exported for other modules.

## Dependencies and Integration Points
Integrated by signature, integrity, key, and crypto consumers that need a stable enum-to-name or enum-to-digest-size mapping. It depends on digest-size macros from `<crypto/hash_info.h>` and kernel symbol exports.

## Risks and Test Signals
The main risk is table drift when new enum members are added or digest constants change. Tests or build-time review should confirm every live enum value has the expected name/size, that absent algorithms remain null/zero by design, and that MD4 intentionally maps to `MD5_DIGEST_SIZE` only because both are 128-bit digests.
