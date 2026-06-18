# sources/distributed-fs/ceph-client/include/crypto/sha2.h

Purpose: declares direct SHA-224, SHA-256, SHA-384, SHA-512, and HMAC helpers plus internal shared SHA-2 block contexts.

Important APIs, types, and flow: constants define digest/block sizes and initial vectors for SHA-2 variants. `crypto_sha256_state`, `sha256_state`, `sha512_state`, block-state structs, and internal `__sha256_ctx`/`__sha512_ctx` share update logic. Public contexts and APIs provide init/update/final/one-shot helpers for SHA-224/256/384/512 and HMAC variants. `sha256_finup_2x()` can finalize two SHA-256 messages from a common context, with `sha256_finup_2x_is_optimized()` reporting optimized support.

State and persistence: caller-owned contexts contain hash or HMAC key state. No persistence exists; HMAC contexts are sensitive.

Dependencies and integration: direct SHA-2 helpers are used by protocol and crypto code needing low-overhead hashing or HMAC without transform allocation. Optimized implementations may be architecture-specific.

Risks and test signals: risks include shared internal update-state mistakes, length-counter overflow, HMAC key preprocessing bugs, and optimized two-message finalization divergence. Signals include NIST SHA-2 and HMAC vectors, empty-message constants, incremental split tests, 2x finup parity, large-message length tests, and generic vs optimized comparisons.
