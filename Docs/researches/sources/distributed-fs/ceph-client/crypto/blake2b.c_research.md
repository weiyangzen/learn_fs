<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blake2b.c -->
# sources/distributed-fs/ceph-client/crypto/blake2b.c

## Purpose

`blake2b.c` registers keyed and unkeyed BLAKE2b shash algorithms for 160-, 256-, 384-, and 512-bit digests. It is a Crypto API wrapper around the library BLAKE2b implementation rather than a standalone compression implementation.

## Important APIs, Types, and Flow

`struct blake2b_tfm_ctx` stores an optional key and key length per transform. `crypto_blake2b_setkey()` validates the maximum key length and copies the key into the transform context. `crypto_blake2b_init()` initializes the per-request `struct blake2b_ctx` with the requested digest size and optional key. `update`, `final`, and one-shot `digest` delegate to `blake2b_update()`, `blake2b_final()`, and `blake2b()`.

The `BLAKE2B_ALG` macro defines four `shash_alg` entries with `CRYPTO_ALG_OPTIONAL_KEY`, driver names ending in `-lib`, priority 300, block size `BLAKE2B_BLOCK_SIZE`, and descriptor size `sizeof(struct blake2b_ctx)`.

## State, Dependencies, and Integration

Persistent state is only the optional key in the tfm context. Streaming hash state lives in the shash descriptor. The file depends on `<crypto/blake2b.h>` and Crypto API shash registration. Consumers select names such as `blake2b-256` or `blake2b-512`.

## Risks and Test Signals

Risks are limited but security-sensitive: key length enforcement, correct digest-size binding per algorithm name, and zeroization expectations for keyed transforms. Test signals include known-answer vectors for all digest sizes, keyed and unkeyed operation, streaming versus one-shot equivalence, and rejection of oversized keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/blake2b.c -->
