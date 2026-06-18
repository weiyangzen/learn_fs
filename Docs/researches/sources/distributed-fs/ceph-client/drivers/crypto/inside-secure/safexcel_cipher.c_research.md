# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_cipher.c Research

## Purpose
`safexcel_cipher.c` registers and implements the Inside Secure/Marvell EIP197/EIP96 symmetric cipher and AEAD Crypto API algorithms. It covers skcipher AES/DES/3DES/SM4/ChaCha20 modes, combined `authenc(hmac(...),...)` AEAD modes, XTS, GCM, CCM, ChaCha20-Poly1305, SM4+SM3 fallbacks, and IPsec wrappers such as RFC4106 GCM, RFC4543 GMAC, and RFC4309 CCM. The file translates Linux Crypto API requests into Safexcel command/result descriptors, token streams, context records, DMA mappings, and completion callbacks.

## Important APIs, Types, and Functions
The main per-transform state is `struct safexcel_cipher_ctx`, which embeds `struct safexcel_context`, the driver-private pointer, cipher mode and algorithm selectors, AEAD flags, IV/counter handling fields, key storage, HMAC/XCM hash metadata, and an optional AEAD fallback transform. Per-request state is `struct safexcel_cipher_req`, carrying encrypt/decrypt direction, result descriptor count, invalidation state, and mapped source/destination entry counts.

`safexcel_skcipher_iv()`, `safexcel_skcipher_token()`, `safexcel_aead_iv()`, and `safexcel_aead_token()` build the EIP197 token program. They handle inline IVs, RFC3686 nonces, ChaCha counters, CBC IVs, ESP IV skipping, CCM B0 construction, AAD hashing, ICV append/retrieve/verify, GCM/CCM `enc(Y0)`, and GMAC no-crypto cases.

`safexcel_skcipher_aes_setkey()`, `safexcel_skcipher_aesctr_setkey()`, `safexcel_skcipher_aesxts_setkey()`, DES/3DES/SM4 setkey helpers, `safexcel_aead_setkey()`, `safexcel_aead_gcm_setkey()`, `safexcel_aead_ccm_setkey()`, and ChaCha-Poly setkey helpers validate keys, expand AES keys where needed, extract RFC nonces, precompute GHASH or HMAC state, and mark cached contexts for invalidation when key material changes.

`safexcel_context_control()` is the central hardware context word builder. It selects crypto algorithm, mode, key size, hash/HMAC/XCM digest mode, and operation type according to `struct safexcel_cipher_ctx` and request direction. `safexcel_send_req()` maps scatterlists, writes command descriptors, writes result descriptors, attaches request tracking to the first result descriptor, and rolls descriptor write pointers and DMA maps back on failure.

`safexcel_queue_req()` allocates the context record, chooses a ring, optionally schedules a TRC-cache invalidation, enqueues the Crypto API request, and starts ring work. `safexcel_skcipher_send()`, `safexcel_aead_send()`, `safexcel_skcipher_handle_result()`, and `safexcel_aead_handle_result()` are the `safexcel_context` callbacks used by the common ring engine.

The many `struct safexcel_alg_template` instances expose the actual Crypto API algorithms, including `ecb(aes)`, `cbc(aes)`, `rfc3686(ctr(aes))`, DES/3DES ECB/CBC, AES-XTS, AES-GCM/CCM, AES/3DES/DES authenc variants with MD5/SHA1/SHA2, ChaCha20, RFC7539 ChaCha20-Poly1305 and ESP, SM4 ECB/CBC/CTR, SM4 authenc SHA1/SM3, and IPsec GCM/CCM variants.

## Control Flow
For skcipher requests, Crypto API `encrypt` or `decrypt` calls `safexcel_queue_req()`. The queue path selects or reuses a hardware ring and context record, marks invalidation if the context cache is stale, enqueues the async request, and schedules ring work. The send callback either emits an invalidate descriptor or calls `safexcel_send_req()`. That function maps input/output scatterlists, preserves CBC decrypt IVs before in-place overwrite, copies key and HMAC state into the context record, emits command descriptors over source SG segments, emits result descriptors over destination SG segments, and programs the first descriptor with context control and tokens.

Completion drains the expected result descriptors, checks hardware errors through `safexcel_rdesc_check_errors()`, completes the hardware ring, unmaps DMA, updates CBC encrypt IV from the final ciphertext block, and completes the Crypto API request. If the request was an invalidation, `safexcel_handle_inv_result()` either frees the context during transform exit or requeues the original request on a selected ring.

AEAD control flow is similar but adjusts source/destination lengths for associated data and authentication tags. Encrypt adds the digest to output; decrypt consumes the tag and verifies it. CCM, GCM, ESP, and GMAC change token sequencing and association length handling. The small/unsupported ChaCha-Poly and SM4-SM3 edge cases use fallback AEAD transforms rather than hardware.

## State and Persistence
Persistent state lives in each Crypto API transform context: selected algorithm/mode, expanded or raw key material, nonce, precomputed HMAC ipad/opad or GHASH state in the embedded `safexcel_context`, and the DMA-backed hardware context record. Request-local state tracks descriptor counts and DMA mapping counts so completion can unmap exactly what was mapped. Hardware context records are allocated from `priv->context_pool` and invalidated before reuse or exit when `EIP197_TRC_CACHE` is active.

No filesystem state is persisted. The relevant long-lived state is kernel memory, DMA mappings, hardware descriptor rings, and the registered Crypto API algorithm table.

## Dependencies and Integration Points
This file depends on the Safexcel core in `safexcel.h`, ring helpers in `safexcel_ring.c`, shared descriptor helpers such as `safexcel_add_cdesc()`, `safexcel_add_rdesc()`, `safexcel_rdr_req_set()`, `safexcel_complete()`, and `safexcel_invalidate_cache()`, and hash support through `safexcel_hmac_setkey()`. It integrates with Linux Crypto API `skcipher` and `aead`, DMA mapping, scatterlist helpers, AES/DES/SM4/ChaCha/GCM/CCM/Authenc validators, and fallback allocation through `crypto_alloc_aead()`.

## Risks and Edge Cases
Descriptor and DMA rollback is high risk: every failure path must undo command descriptors, result descriptors, and SG mappings consistently. AEAD length arithmetic is sensitive because assoclen, digest size, ESP IV skip, and decrypt tag removal interact. Several hardware limitations are handled explicitly: zero-length input gets a dummy descriptor, EIP96 SM4 blocksize errors are checked in software, ChaCha-Poly and SM4-SM3 use fallback for zero or small corner cases, and TRC-cache invalidation is required after key/state changes. Unaligned nonce loads through pointer casts and endianness conversions are correctness-sensitive. The XTS path rejects short data but still relies on correct key split and tweak-key placement.

## Test Signals
Useful tests are Crypto API self-tests and tcrypt vectors for all registered algorithm names and driver names, including in-place and out-of-place SG lists, multi-SG boundaries, zero-length and AAD-only AEAD cases, CBC IV update semantics, authentication failure on decrypt, RFC4106/RFC4309 assoclen validation, SM4 blocksize rejection, XTS short input rejection, and fallback-triggering ChaCha-Poly/SM4-SM3 cases. Runtime signals include hardware result descriptor errors, DMA mapping failures, invalidation warnings during transform exit, and request completion status under ring pressure.
