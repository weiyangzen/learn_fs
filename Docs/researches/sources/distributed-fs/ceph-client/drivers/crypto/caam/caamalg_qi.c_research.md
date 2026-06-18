# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi.c

## Purpose

`caamalg_qi.c` registers and implements kernel crypto API algorithms backed by CAAM's DPAA 1.x Queue Interface. It is the QI frontend for skcipher and AEAD algorithms: it validates and stores keys, builds CAAM shared descriptors via `caamalg_desc.c`, lazily creates QI driver contexts, maps crypto request scatterlists into QMan scatter/gather tables, enqueues requests with `caam_qi_enqueue()`, and completes asynchronous crypto API requests from CAAM callbacks.

The file covers synchronous-looking crypto API entry points that return `-EINPROGRESS` after successful enqueue. It handles AES/DES/3DES CBC, AES CTR and RFC3686 CTR, AES XTS with fallback cases, generic AES/DES/3DES authenc HMAC-CBC combinations, AES-GCM, RFC4106 GCM, and RFC4543 GMAC.

## Important APIs, types, and structures

- `CAAM_CRA_PRIORITY`, `CAAM_MAX_KEY_SIZE`, `DESC_MAX_USED_BYTES`, and `DESC_MAX_USED_LEN` set algorithm priority and per-transform key/descriptor storage limits.
- `struct caam_alg_entry` stores CAAM class 1/class 2 algorithm selectors plus mode flags: `rfc3686`, `geniv`, and `nodkp`.
- `struct caam_aead_alg` and `struct caam_skcipher_alg` wrap kernel `aead_alg`/`skcipher_alg` objects with CAAM metadata and a registration flag for clean teardown.
- `struct caam_ctx` is the per-transform context. It owns the job ring device, encryption/decryption shared descriptors, key buffer and DMA address, DMA direction, class 1/class 2 `alginfo`, auth size, QI device, a spinlock for lazy driver context initialization, per-operation `caam_drv_ctx` handles, and XTS fallback state.
- `struct caam_skcipher_req_ctx` holds fallback request state for XTS software fallback.
- `struct aead_edesc` and `struct skcipher_edesc` are per-request extended descriptors allocated from the QI cache. They hold mapped scatterlist counts, IV and QMan SG DMA addresses, AEAD assoclen DMA mapping, callback request state, and inline QMan SG entries.

Key setup and descriptor functions:

- `aead_set_sh_desc()`, `gcm_set_sh_desc()`, `rfc4106_set_sh_desc()`, and `rfc4543_set_sh_desc()` choose inline versus DMA keys, compute IV/nonce offsets, and call the matching shared descriptor constructors.
- `aead_setkey()` parses `authenc` keys, uses DKP on SEC era >= 6 or `gen_split_key()` on older eras, lays out auth split key plus encryption key in `ctx->key`, DMA-syncs key material, builds descriptors, and updates existing driver contexts.
- `des3_aead_setkey()` adds 3DES key verification before delegating to authenc setup.
- `gcm_setkey()`, `rfc4106_setkey()`, and `rfc4543_setkey()` validate AES key lengths, handle IPsec salt in the last four bytes for RFC4106/RFC4543, DMA-sync key material, rebuild descriptors, and update driver contexts.
- `skcipher_setkey()` and wrappers (`aes_skcipher_setkey()`, `rfc3686_skcipher_setkey()`, `ctr_skcipher_setkey()`, `des3_skcipher_setkey()`, `des_skcipher_setkey()`, `xts_skcipher_setkey()`) validate keys and build shared descriptors for skcipher modes. XTS also configures software fallback for unsupported eras or key sizes.

Request path functions:

- `get_drv_ctx()` lazily creates a `caam_drv_ctx` for encrypt or decrypt under `ctx->lock`, binding it to the current shared descriptor and QI device.
- `caam_unmap()`, `aead_unmap()`, and `skcipher_unmap()` centralize DMA unmapping for source/destination scatterlists, IV buffers, QMan SG tables, and AEAD assoclen.
- `aead_edesc_alloc()` maps AEAD src/dst scatterlists, copies IV into DMA-able memory when required, maps the big-endian assoclen word, builds the QMan SG input layout `[assoclen, optional IV, src]`, builds output SG entries for in-place or separate destination, and attaches the driver callback.
- `aead_crypt()`, `aead_encrypt()`, `aead_decrypt()`, `ipsec_gcm_encrypt()`, and `ipsec_gcm_decrypt()` check congestion and IPsec assoclen rules, allocate an edesc, enqueue the request, and return `-EINPROGRESS` on success.
- `aead_done()` translates CAAM status with `caam_jr_strstatus()`, unmaps resources, completes the AEAD request, and frees the edesc.
- `skcipher_edesc_alloc()` maps skcipher scatterlists, creates overlapping or separate QMan SG tables in the form `[IV, src]` and `[dst, IV]`, maps a DMA-able IV buffer bidirectionally, and prepares the driver request.
- `skcipher_crypt()`, `skcipher_encrypt()`, and `skcipher_decrypt()` handle zero-length behavior, XTS fallback routing, congestion, edesc allocation, enqueue, and cleanup on enqueue failure.
- `skcipher_done()` decodes CAAM status, unmaps DMA resources, copies the resulting IV/counter/tweak state back into `req->iv` when successful, frees the edesc, and completes the request.

Registration functions:

- `driver_algs[]` declares QI skcipher algorithms: `cbc(aes)`, `cbc(des3_ede)`, `cbc(des)`, `ctr(aes)`, `rfc3686(ctr(aes))`, and `xts(aes)`.
- `driver_aeads[]` declares QI AEAD algorithms: `rfc4106(gcm(aes))`, `rfc4543(gcm(aes))`, `gcm(aes)`, and a matrix of `authenc(hmac(md5/sha1/sha224/sha256/sha384/sha512),cbc(aes/des3_ede/des))` with generated-IV `echainiv(...)` variants.
- `caam_init_common()`, `caam_cra_init()`, and `caam_aead_init()` allocate a job ring, map per-transform key storage, initialize `alginfo` algorithm selectors, set DMA direction for DKP-capable AEAD, initialize locks/context slots, and allocate XTS fallback transforms.
- `caam_exit_common()`, `caam_cra_exit()`, `caam_aead_exit()`, and `caam_qi_algapi_exit()` release driver contexts, unmap key storage, free job rings, free fallback transforms, and unregister algorithms.
- `caam_skcipher_alg_init()` and `caam_aead_alg_init()` fill common crypto API metadata such as module, priority, context size, async/allocation flags, and init/exit hooks.
- `caam_qi_algapi_init()` gates QI registration to DPAA 1.x QI, reads CAAM hardware capability registers, filters algorithms by AES/DES/MD availability and digest-size limits, registers supported algorithms, and logs when registration succeeds.

## Control flow

Per-transform initialization starts when the crypto API instantiates an algorithm. The init hook allocates a CAAM job ring so requests for that transform preserve ordering, maps the context key buffer for DMA, sets class 1/class 2 algorithm types, and initializes per-operation driver context pointers to `NULL`. XTS additionally allocates a fallback transform.

When users set a key or authsize, the file validates input, writes key material into `ctx->key` or uses the provided key pointer for inline skcipher descriptors, chooses descriptor inline-key mode, and calls `caamalg_desc.c` constructors to fill `ctx->sh_desc_enc` and `ctx->sh_desc_dec`. If a QI driver context already exists for encryption or decryption, it is updated in place with `caam_drv_ctx_update()` so subsequent requests use the new descriptor.

At request time, `aead_crypt()` or `skcipher_crypt()` first rejects congested CAAM queues with `-EAGAIN`. It allocates an edesc from the QI cache, maps scatterlists according to in-place versus out-of-place operation, builds QMan SG entries expected by the QI shared descriptors, and submits `edesc->drv_req` through `caam_qi_enqueue()`. A zero return from enqueue means ownership transferred to CAAM/QI and the crypto API sees `-EINPROGRESS`; a nonzero return triggers immediate unmap/free.

On completion, QI invokes `aead_done()` or `skcipher_done()`. The callbacks translate CAAM status into a Linux error code, unmap all DMA resources, perform mode-specific completion work such as copying skcipher IV state back to `req->iv`, free the QI cache allocation, and call the crypto API completion callback.

At module/driver startup, `caam_qi_algapi_init()` detects the CAAM era/capabilities, skips unsupported algorithms, initializes common fields, and registers algorithms with the kernel crypto API. Exit unregisters only entries whose `registered` flag was set.

## State and persistence behavior

Persistent per-transform state lives in `struct caam_ctx`. It includes shared descriptors, key material, DMA mapping for that key buffer, auth size, algorithm metadata, fallback transform, and lazily initialized QI driver contexts. This state persists from crypto transform init until exit. Key setup mutates descriptors and key storage; existing driver contexts are explicitly updated to keep long-lived QI contexts coherent.

Per-request state lives in `aead_edesc` or `skcipher_edesc` allocated from `qi_cache_alloc()`. These objects persist only until CAAM completion or enqueue failure cleanup. They own all request DMA mappings, QMan SG tables, copied IV buffers, AEAD assoclen DMA storage, and the callback wrapper.

The file also mutates global algorithm registration state through the `registered` booleans in the static algorithm arrays. It reads global/device state such as `caam_congested`, `caam_dpaa2`, hardware performance/version registers, and `priv->era`/`priv->qi_present`, but it does not persist request data globally.

Security-sensitive state includes `ctx->key` and temporary parsed `crypto_authenc_keys`. The authenc parser output is cleared with `memzero_explicit()`, but `ctx->key` persists for the transform lifetime and is DMA-mapped.

## Dependencies and integration points

This file integrates several layers:

- Kernel crypto API: `struct crypto_aead`, `struct crypto_skcipher`, `aead_request`, `skcipher_request`, algorithm registration/unregistration, key verification helpers, authsize checks, fallback transforms, and async request completion.
- CAAM core/job-ring/QI: `caam_jr_alloc()`, `caam_jr_free()`, `caam_drv_ctx_init()`, `caam_drv_ctx_update()`, `caam_drv_ctx_rel()`, `caam_qi_enqueue()`, `caam_jr_strstatus()`, QI cache allocation, QMan SG entry helpers, and global congestion state.
- Descriptor construction: all shared descriptors are produced by the functions declared in `caamalg_desc.h`.
- DMA and scatterlist APIs: `sg_nents_for_len()`, `dma_map_sg()`, `dma_unmap_sg()`, `dma_map_single()`, `dma_sync_single_for_device()`, and QMan SG conversion helpers.
- CAAM hardware capability registers: era-specific CHA/version registers determine AES/DES/MD availability and digest-size limits.
- XTS fallback: Linux software or other non-CAAM fallback is used for older SEC eras with upper IV half set, and for unsupported XTS key sizes.

The QI frame layout built here is tightly coupled to the `is_qi = true` descriptor variants. AEAD input starts with a DMA-mapped 4-byte assoclen, may include a DMA-mapped IV, then the source data. Skcipher input starts with IV then source data, and output ends with the IV buffer so the descriptor can store the updated chaining state.

## Risks and edge cases

- DMA cleanup paths are complex. Every failure after partial mapping must unmap only what was actually mapped; leaks or double unmaps would be hard to debug under load.
- The QMan SG table padding rules are hardware-specific because CAAM reads four SG entries at a time. Incorrect padding can cause hardware overreads past the SG table.
- AEAD in-place and out-of-place length calculations differ around authentication tag length. Encrypt includes authsize in output; decrypt subtracts it. Incorrect `cryptlen` assumptions would produce insufficient SG errors or memory corruption.
- `get_drv_ctx()` stores `ERR_PTR` values in `ctx->drv_ctx[type]` if initialization fails. Later calls will return the same error until transform teardown; this is intentional but makes transient QI init failures sticky.
- Key layout for authenc, RFC3686, RFC4106, and RFC4543 is subtle. Salt/nonce bytes are part of user key material but not always part of the AES key length used by descriptors and DMA sync.
- `rfc4106_setkey()` and `rfc4543_setkey()` subtract four from `keylen` before validating; callers are expected to satisfy crypto API minimum key sizes, but malformed short lengths would be dangerous if validation did not catch them through unsigned arithmetic behavior.
- Debug key dumps can expose plaintext key material in debug logs if enabled.
- XTS fallback selection depends on SEC era, IV upper half, and key size. Divergence between CAAM and fallback behavior can appear only for specific tweak/key combinations.
- `caam_congested` returns `-EAGAIN` before allocation; callers must be ready to retry.
- Algorithm registration is capability-filtered. Systems without MD, AES, DES, GCM-capable AES, or sufficient digest size will silently skip subsets of declared algorithms.
- The per-transform job ring allocation is intended to preserve per-transform request ordering; changing this policy could affect chained modes and crypto API ordering expectations.

## Test signals

Strong signals include successful QI algorithm registration in `/proc/crypto`, kernel crypto self-tests for each registered `cra_driver_name`, tcrypt or AF_ALG tests covering in-place and out-of-place scatterlists, multi-segment SG inputs requiring QMan SG padding, zero-length and tag-only AEAD cases, GCM/RFC4106/RFC4543 authsize validation, IPsec assoclen validation, RFC3686 nonce/counter continuation tests, XTS fallback tests on era <= 8 and unsupported key sizes, forced `caam_qi_enqueue()` failure cleanup tests, and dynamic-debug descriptor/key path inspection on non-production keys. DMA debug and KASAN/KMSAN are especially useful for edesc cleanup and SG layout regressions.
