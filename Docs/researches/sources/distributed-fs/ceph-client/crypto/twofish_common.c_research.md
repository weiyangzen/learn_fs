# sources/distributed-fs/ceph-client/crypto/twofish_common.c

## Purpose
This file provides the shared Twofish key schedule used by both generic C and architecture-specific cipher implementations. It owns the precomputed q permutations, MDS tables, finite-field exponent tables, key-dependent S-box generation, whitening subkey generation, and round subkey generation. The exported entry points are `__twofish_setkey()` for direct context setup and `twofish_setkey()` for the legacy `crypto_tfm` cipher API.

## Important APIs, Types, And Functions
The important external type is `struct twofish_ctx` from `<crypto/twofish.h>`, with `s`, `w`, and `k` arrays populated by the key schedule. `__twofish_setkey()` validates only that `key_len` is a multiple of 8, then handles the 16, 24, and 32 byte Twofish key sizes through separate macro paths. `twofish_setkey()` is a thin adapter using `crypto_tfm_ctx()`. The `CALC_S`, `CALC_SB_*`, and `CALC_K*` macros encode most of the algorithm and are coupled tightly to the table layout.

## Control Flow
Setup computes RS-derived S-vector bytes from the raw key, conditionally extending them for 192-bit and 256-bit keys. It then fills all four key-dependent S-box tables for 256 entries and computes eight whitening words plus 32 round subkeys. The 128-, 192-, and 256-bit branches differ by q-table depth and by which key bytes feed the h-function.

## State, Dependencies, Integration, Risks, And Tests
The only persistent state is the caller-owned `twofish_ctx`; all other state is static read-only tables or stack temporaries. It integrates with the kernel CryptoAPI and is consumed by `twofish_generic.c` and accelerated Twofish implementations. The main risks are table/macro transcription errors, accepting unsupported 8-byte multiples if callers bypass CryptoAPI min/max key checks, and side-channel exposure from key-dependent table lookups. Test signals are CryptoAPI twofish known-answer tests for 128/192/256-bit keys, invalid key length tests, module load/unload, and cross-comparison with accelerated implementations.
