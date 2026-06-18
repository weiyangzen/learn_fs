# sources/distributed-fs/ceph-client/crypto/lrw.c

Purpose: implements the LRW block-cipher mode template for 128-bit block ciphers, mainly for disk-style tweakable encryption. It wraps an ECB child cipher and applies GF(2^128) tweak masks before and after the child operation.

Important APIs, types, and functions: `struct lrw_tfm_ctx` stores the child skcipher, a `gf128mul_64k` table for key2, and `mulinc[128]` tweak increments. `struct lrw_request_ctx` stores the starting tweak and child request. Key and data paths are `lrw_setkey()`, `lrw_xor_tweak()`, `lrw_init_crypt()`, `lrw_encrypt()`, and `lrw_decrypt()`. Template setup is in `lrw_create()`.

Control flow: `lrw_create()` grabs the requested child or automatically wraps a bare block cipher as `ecb(cipher)`, then requires a 16-byte block size and zero child IV. `lrw_setkey()` splits the supplied key into child key plus final 16-byte tweak key, builds the GF multiplication table, and precomputes increment masks. Encryption and decryption compute initial `T = IV * key2`, xor each block with the tweak, run the child over the destination buffer, then recompute and xor the same tweak stream after the child operation.

State and persistence: transform state persists the child handle and GF tables until `lrw_exit_tfm()`. Request state holds only the current initial tweak and child request. The IV is advanced on the second pass at completion so callers see the consumed counter.

Dependencies and integration points: depends on `crypto/internal/skcipher.h`, `crypto/b128ops.h`, `crypto/gf128mul.h`, `skcipher_walk_virt()`, and the crypto template registry. It soft-depends on `ecb`.

Risks: bit numbering in `lrw_setbit128_bbe()` is endian-sensitive. The key length contract requires at least child minimum plus 16 bytes. The two-pass tweak recomputation must remain identical, or encryption/decryption corrupts data. LRW is a legacy disk mode; new code usually prefers XTS where applicable.

Test signals: known LRW vectors from tcrypt, non-in-place and in-place SG tests, IV advancement checks, child lookup with both `cipher` and `ecb(cipher)` names, key-size boundary tests, and big-endian build coverage are valuable.
