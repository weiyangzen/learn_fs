# sources/distributed-fs/ceph-client/crypto/xxhash_generic.c

## Purpose
This file exposes the kernel `lib/xxhash.c` 64-bit non-cryptographic hash through the shash API as `xxhash64` and `xxhash64-generic`.

## Important APIs, Types, And Functions
`struct xxhash64_tfm_ctx` stores the optional 64-bit seed. `struct xxhash64_desc_ctx` stores streaming `xxh64_state`. `xxhash64_setkey()` accepts exactly eight little-endian seed bytes. `xxhash64_init()`, `xxhash64_update()`, and `xxhash64_final()` implement streaming shash operation, while `xxhash64_digest()` uses the one-shot `xxh64()` helper.

## Control Flow
Setkey initializes the transform seed when provided. Streaming users reset descriptor state from that seed, feed arbitrary byte ranges through `xxh64_update()`, and emit the digest as little-endian. One-shot users bypass descriptor accumulation and hash the full input directly with the transform seed.

## State, Dependencies, Integration, Risks, And Tests
State is split between per-transform seed and per-request streaming state. The algorithm is marked `CRYPTO_ALG_OPTIONAL_KEY`, so the default zero seed is valid. Dependencies are `<linux/xxhash.h>`, shash registration, and unaligned little-endian helpers. Risks are misuse as a cryptographic hash, seed-endian mismatch, and divergence between streaming and one-shot paths. Test signals are xxHash64 reference vectors, optional-key behavior, invalid key length, and streaming versus digest equivalence over split inputs.
