# sources/distributed-fs/ceph-client/crypto/sha3.c

Purpose: registers library-backed SHA3-224, SHA3-256, SHA3-384, and SHA3-512 shash algorithms.

Important APIs and functions: init wrappers call `sha3_224_init()`, `sha3_256_init()`, `sha3_384_init()`, or `sha3_512_init()`. Shared update/final wrappers call `sha3_update()` and `sha3_final()`. Digest wrappers call the corresponding one-shot library functions. `crypto_sha3_export_core()` and `crypto_sha3_import_core()` copy the full `struct sha3_ctx`.

Control flow: module init registers four algorithms with digest sizes, block sizes, descriptor size, and core export/import callbacks. Runtime requests are direct library delegations. Unlike SHA-1/SHA-2 wrappers, there is no extra shash state format with partial-byte trailer; core export/import copies the whole sponge state.

State and persistence: descriptor context stores `struct sha3_ctx` for each request. No tfm key state exists. Algorithm registration persists while loaded.

Dependencies and integration points: depends on `<crypto/sha3.h>` and crypto shash internals. SHA3 names are also referenced by RSA PKCS#1 hash-prefix template support.

Risks: full-context copy export/import must remain valid if `struct sha3_ctx` changes. SHA-3 rate/block sizes differ by digest variant, so table entries must match library constants. There is no HMAC-SHA3 wrapper here.

Test signals: FIPS 202 known-answer vectors for all four variants, split update versus one-shot digest, core export/import resume, registration aliases, and PKCS#1 verification with SHA3-256/384/512.
