# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/safexcel_hash.c Research

## Purpose
`safexcel_hash.c` implements Inside Secure/Marvell Safexcel asynchronous hash and MAC algorithms for the Linux Crypto API. It supports plain MD5, SHA1, SHA224, SHA256, SHA384, SHA512, SM3, SHA3 variants, HMAC variants for those hashes, AES CBC-MAC, XCBC, and CMAC. It translates `ahash_request` operations into Safexcel descriptor/token programs, handles partial-block caching and hash continuation, and supplies fallback paths where the hardware cannot support streaming, import/export, or zero-length SHA3/HMAC-SHA3 cases.

## Important APIs, Types, and Functions
`struct safexcel_ahash_ctx` holds per-transform state: embedded `safexcel_context`, selected hardware hash algorithm, key size, CBC/XCBC flags, fallback state, AES key schedule pointer for XCBC/CMAC, fallback `crypto_ahash`, prehash `crypto_shash`, and shash descriptor. `struct safexcel_ahash_req` is request-local DMA-aligned state containing flags for finish/HMAC/invalidation/fallback quirks, mapped SG/result/cache DMA addresses, digest type, state and block sizes, current hash state, total and processed lengths, and two cache buffers.

`safexcel_hash_token()` builds a four-token hash program: consume input through the hash engine, optionally pad CBC-MAC to a block boundary, insert output digest, then NOP. `safexcel_context_control()` programs the hardware context for initial hash, continuation, HMAC, XCM MACs, precomputed digest state, digest counters, and no-finish operations.

`safexcel_ahash_cache()`, `safexcel_ahash_update()`, `safexcel_ahash_final()`, `safexcel_ahash_finup()`, `safexcel_ahash_export()`, and `safexcel_ahash_import()` implement the Crypto API request lifecycle. `safexcel_ahash_send_req()` maps cache/current SG data into command descriptors, emits one result descriptor for the digest state, and updates `processed`. `safexcel_handle_req_result()` unmaps DMA, performs HMAC outer-pass continuation when needed, copies final digests, and moves deferred cache bytes.

HMAC key support is split across `safexcel_hmac_init_pad()`, `safexcel_hmac_init_iv()`, `__safexcel_hmac_setkey()`, and exported `safexcel_hmac_setkey()`, which is also used by cipher AEAD setkey code. CBC-MAC/XCBC/CMAC setkey paths precompute AES-based key material for XCM digest operation. SHA3 and HMAC-SHA3 use `safexcel_sha3_*` and `safexcel_hmac_sha3_*` wrappers with `crypto_alloc_ahash()` fallback.

## Control Flow
`init` functions zero request state, set algorithm selectors, digest mode, digest size, state size, block size, and HMAC starting state. `update` first tries to cache data until enough bytes exist for a hardware block. If the cache overflows or this is the last request, it enqueues the request to the Safexcel ring. The send callback either emits a cache invalidation descriptor or constructs command descriptors over cached bytes plus SG bytes. For non-final updates, the code keeps one block cached so final padding remains correct.

On completion, the result descriptor is checked, DMA mappings are undone, and the hardware-produced digest state is kept in `req->state`. Final HMAC may require a second internal hash pass when the hardware cannot perform the direct HMAC finish, so completion rewrites request state with opad and re-enqueues without completing the original request. Final plain hashes copy the digest from request state to `areq->result`.

Zero-length hashes are handled in software for MD5/SHA1/SHA2/SM3 using known constants. Zero-length CBC-MAC/XCBC/CMAC and zero-length HMAC have special synthetic states or padding. SHA3 update/final/export/import routes to fallback because hardware is only used for single non-empty digest/finup style flows.

## State and Persistence
The transform context persists hardware context records, HMAC ipad/opad state, fallback transforms, and AES key schedules. Request state persists rolling hash state, byte counters, deferred block cache, and DMA addresses between update/final calls. Context records are DMA pool allocations and may require TRC-cache invalidation when continuation state or HMAC outer state changes. No filesystem state is persisted.

## Dependencies and Integration Points
The file integrates with Linux `ahash`, `shash`, AES helper APIs, HMAC constants, scatterlist copying, DMA mapping, and Safexcel ring/core functions. It exports `safexcel_hmac_setkey()` to the cipher/AEAD file so combined authenc algorithms can reuse the same HMAC precompute logic. SHA3/HMAC-SHA3 fallback depends on generic Crypto API implementations of the same algorithm names.

## Risks and Edge Cases
Partial-block caching and length accounting are the main correctness risks: `len`, `processed`, `cache`, and `cache_next` must stay consistent across update/final/import/export. HMAC continuation has hardware-specific limitations, including fake outer passes, zero-length HMAC padding, digest counters with a 32-bit hardware limit, and TRC invalidation when state changes. CBC-MAC/XCBC/CMAC have custom padding and AES subkey transformations where endianness matters. SHA3 fallback state is subtle because some operations begin on hardware but update/export/import force fallback. DMA rollback must cover cache, SG, result mapping, and descriptor write pointers.

## Test Signals
Use Crypto API self-tests and known-answer tests for plain hashes, HMACs, SM3, SHA3, CBC-MAC, XCBC, and CMAC. Important cases include zero-length digest and HMAC, repeated small updates, updates crossing block size, import/export after partial updates, long inputs near digest counter limits, multi-SG requests, callback completion after requeued HMAC outer pass, SHA3 fallback after update/export/import, and context invalidation under repeated setkey or continuation.
