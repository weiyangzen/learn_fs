# subset-b-001217 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_desc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_desc.c

## Purpose

`caamalg_desc.c` is the shared descriptor construction library for the Freescale/NXP CAAM crypto driver. It does not execute requests directly. Instead, it emits CAAM descriptor words into caller-owned `u32` buffers for AEAD, GCM/IPsec GCM/GMAC, ChaCha20-Poly1305, skcipher, XTS, protected-blob key decapsulation, and one protected-key skcipher job descriptor. These descriptors are later installed into job-ring or Queue Interface driver contexts by higher-level CAAM algorithm files such as `caamalg_qi.c`.

The file is hardware-facing glue: most logic is sequencing CAAM class 1 cipher engines, class 2 authentication engines, descriptor math registers, variable-length FIFO loads/stores, key loading, IV/counter layout, and erratum workarounds. Exported functions are small public construction entry points, while static helpers factor common AEAD/skcipher descriptor fragments.

## Important APIs and functions

- `aead_append_src_dst()` appends the common AEAD payload store/load pair: write message data to output and load variable-length data to class 1/class 2 using the requested FIFO message type.
- `append_dec_op1()` emits class 1 decrypt operations. For AES descriptors that may be shared it conditionally emits a DK-bit variant when the descriptor is already shared; non-AES algorithms use a normal init-final decrypt operation.
- `cnstr_shdsc_aead_null_encap()` and `cnstr_shdsc_aead_null_decap()` build null-encryption ESP-style HMAC descriptors, including split-key or DKP auth key handling, variable-length assoc+payload movement, descriptor self-patching for older hardware without `MOVE_LEN`, and ICV write/read.
- `init_sh_desc_key_aead()` initializes shared AEAD descriptors with saved context, loads auth and cipher keys, handles SEC era differences for DKP versus precomputed split keys, and preloads RFC3686 nonces into class 1 context.
- `cnstr_shdsc_aead_encap()`, `cnstr_shdsc_aead_decap()`, and `cnstr_shdsc_aead_givencap()` build generic authenc descriptors for encryption, decryption, and generated-IV encryption. They support QI-specific assoclen/IV input format, RFC3686 counter setup, generated chained IV output, and class 1/class 2 sequencing.
- `cnstr_shdsc_gcm_encap()` and `cnstr_shdsc_gcm_decap()` build generic AES-GCM descriptors with zero-associated-data and zero-payload branches, QI IV loading, tag write or verification, and optional inline/DMA key forms.
- `cnstr_shdsc_rfc4106_encap()` and `cnstr_shdsc_rfc4106_decap()` build IPsec ESP GCM descriptors where salt is appended to key material and IV is part of AAD. They include a workaround for CAAM erratum A-005473 around simultaneous sequence FIFO skips.
- `cnstr_shdsc_rfc4543_encap()` and `cnstr_shdsc_rfc4543_decap()` build IPsec GMAC descriptors that authenticate assoc+payload while forwarding payload unchanged through OFIFO, using descriptor self-patching where `MOVE_LEN` is unavailable.
- `cnstr_shdsc_chachapoly()` builds generic RFC7539 and IPsec RFC7634 ChaCha20-Poly1305 descriptors. It loads ChaCha and Poly operations, optionally installs IPsec salt, routes associated data through both class alignment blocks, emits metadata IV for IPsec output, and either writes or verifies the tag.
- `skcipher_append_src_dst()` is the common skcipher variable-length class 1 load/store sequence.
- `cnstr_desc_skcipher_enc_dec()` builds a complete job descriptor for protected-key skcipher operations using external source/destination pointers, protected key DMA address, optional IV load/store, and class 1 operation.
- `cnstr_desc_protected_blob_decap()` builds a job descriptor that converts a CAAM black blob key into a protected key, using `KEYMOD` and optionally jumping to a next descriptor.
- `cnstr_shdsc_skcipher_encap()` and `cnstr_shdsc_skcipher_decap()` build shared skcipher descriptors for CBC/CTR/DES/3DES/ChaCha20-style algorithms, including RFC3686 nonce and counter layout, IV load/store, and ChaCha finalize behavior.
- `cnstr_shdsc_xts_skcipher_encap()` and `cnstr_shdsc_xts_skcipher_decap()` build XTS AES descriptors, install a large sector size to effectively disable CAAM sector segmentation for Linux crypto API/dm-crypt usage, load the two halves of the 16-byte tweak into CAAM context offsets, and store the resulting IV/tweak state.

All construction entry points are exported with `EXPORT_SYMBOL`, so this file is an internal module API for other CAAM algorithm frontends.

## Control flow

Most descriptor constructors follow the same high-level pattern:

1. Initialize a job or shared descriptor with `init_job_desc()` or `init_sh_desc()`, often using `HDR_SHARE_SERIAL` and sometimes `HDR_SAVECTX`.
2. Emit a "skip if already shared" jump around key-loading commands. Shared descriptors are expected to avoid reloading keys after hardware context sharing has already materialized them.
3. Select inline versus DMA key commands based on `struct alginfo` fields supplied by the caller. AEAD auth descriptors use era-specific split key versus DKP behavior.
4. Load QI-specific leading metadata when `is_qi` is true. For AEAD/GCM this usually means reading a 4-byte assoclen into math register 3, waiting for descriptor engine pipeline conditions to clear, and loading IV bytes from the input frame rather than from a job descriptor pointer.
5. Program CAAM math registers such as `VARSEQINLEN`, `VARSEQOUTLEN`, `SEQINLEN`, `SEQOUTLEN`, `REG0`, `REG2`, and `REG3` to drive variable-length FIFO movement.
6. Emit class operations (`append_operation`) for class 1 cipher and class 2 authentication engines in the required order.
7. Emit sequence FIFO loads/stores for associated data, payload, IV, and tag/ICV.
8. Backpatch local jumps and move targets with `set_jump_tgt_here()` or `set_move_tgt_here()`.
9. Dump the descriptor with `print_hex_dump_debug()` for debug builds.

The AEAD authenc path authenticates assoc data before payload, then encrypts/decrypts class 1 data while class 2 writes or verifies the ICV. GCM/RFC4106/RFC4543 paths are class 1 GCM-based and have extra zero-length branches to keep CAAM operation semantics valid when assoc or payload lengths are zero. ChaCha-Poly uses both class 1 and class 2 AEAD operations and an NFIFO path to feed associated data to both engines while forwarding it to output as needed.

## State and persistence behavior

This file maintains no global mutable runtime state. Its persistent effects are the descriptor words written into the caller-provided `desc` buffers and, for job descriptors, embedded DMA addresses and immediate key modifier data. It relies on callers to allocate buffers large enough for the advertised descriptor length macros, preserve key memory for inline immediate emission until descriptor construction finishes, DMA-map any pointer-based key material, and install/update descriptors in CAAM driver contexts.

Within a generated descriptor, CAAM hardware state is deliberately manipulated: class 1/class 2 contexts can be saved across shared descriptor invocations, keys may be loaded once and reused under descriptor sharing, context registers hold IVs/nonces/counters/tweaks, and descriptor math registers hold assoc/payload lengths. These are hardware execution states, not C-side persistent state.

## Dependencies and integration points

The implementation depends heavily on CAAM descriptor builder APIs and hardware constants from `desc_constr.h`, compatibility/types from `compat.h`, and blob protocol constants from `<soc/fsl/caam-blob.h>`. It consumes `struct alginfo` fields such as `algtype`, key virtual/DMA addresses, key lengths, `key_inline`, protected key addresses, `plain_keylen`, and `key_cmd_opt`.

Primary consumers include QI and non-QI CAAM algorithm frontends. In this subset, `caamalg_qi.c` calls the AEAD, GCM, RFC4106, RFC4543, skcipher, and XTS constructors when keys or auth sizes change and then installs the descriptors into QI driver contexts. The header also exposes protected-blob helpers used by protected-key flows elsewhere in the CAAM driver.

The `is_qi` parameter is an important integration boundary: QI descriptors expect a leading assoclen entry and often IV data in the input frame's scatter/gather layout, while non-QI descriptors rely on different job descriptor overrides such as `DPOVRD`. SEC era is another boundary: era < 6 paths require precomputed split auth keys, while newer hardware can use descriptor key protocol (`append_proto_dkp`).

## Risks and edge cases

- Descriptor length accounting is critical. Callers must reserve enough words for selected options such as QI, RFC3686 nonce/counter setup, generated IV, and inline keys.
- Length math depends on CAAM register conventions (`REG0` as zero-sized adjust, `REG3` as assoclen, `SEQINLEN`/`SEQOUTLEN` semantics). A mismatch between caller frame layout and descriptor math can corrupt output, drop authentication data, or misverify tags.
- Several paths self-patch descriptor buffer move lengths to work around hardware revisions without `MOVE_LEN`. The required instruction spacing is subtle and easy to regress.
- RFC3686 and IPsec GCM/GMAC key layouts intentionally treat trailing bytes as nonce/salt. Incorrect `cdata->keylen` or `key_virt` setup by callers would make descriptors read wrong nonce/salt bytes.
- GCM zero-associated-data and zero-payload jumps are correctness-sensitive; off-by-one jump distances would affect empty-message authentication.
- The RFC4106 erratum A-005473 workaround should be preserved when refactoring sequence FIFO skip/store order.
- `append_dec_op1()` has AES-specific DK handling. Using it with wrong `algtype` or wrong context offset selection could produce decrypt operations incompatible with shared AES contexts.
- Debug dumps can expose descriptor contents and possibly inline key material in debug logs if dynamic debug is enabled.
- Protected blob descriptors embed protocol options derived from `key_cmd_opt`; EKT handling and protected key lengths must stay aligned with blob/key management code.

## Test signals

Useful validation signals include kernel crypto API self-tests for every registered CAAM algorithm name, AF_ALG/tcrypt tests for CBC/CTR/RFC3686/XTS and authenc combinations, IPsec ESP tests for RFC4106 and RFC4543 including zero-length payload and AAD-only cases, generated-IV AEAD tests that inspect returned IV/ciphertext layout, SEC era matrix testing for pre-DKP versus DKP split-key behavior, and hardware QI tests that exercise non-contiguous scatterlists. Descriptor debug dumps can be compared against expected command lengths and key-inline decisions, but functional tag verification and IV/counter continuation tests are stronger end-to-end signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_desc.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_desc.h

## Purpose

`caamalg_desc.h` is the public descriptor-construction contract for CAAM AEAD and skcipher algorithm frontends. It publishes conservative descriptor text length macros and prototypes for the constructors implemented in `caamalg_desc.c`. The header lets callers size shared descriptor buffers, run inline-key fit calculations, and call the right constructor for generic authenc, GCM, IPsec GCM/GMAC, ChaCha-Poly, skcipher, XTS, protected blob, and protected-key job descriptor paths.

## Important APIs, constants, and types

- `DESC_AEAD_*`, `DESC_QI_AEAD_*`, and `DESC_AEAD_CTR_RFC3686_LEN` size generic authenc descriptors, including QI variants and extra RFC3686 nonce/counter commands.
- `DESC_AEAD_NULL_*` sizes null-encryption HMAC AEAD descriptors.
- `DESC_GCM_*`, `DESC_QI_GCM_*`, `DESC_RFC4106_*`, `DESC_QI_RFC4106_*`, `DESC_RFC4543_*`, and `DESC_QI_RFC4543_*` size GCM, IPsec GCM, and IPsec GMAC descriptors.
- `DESC_SKCIPHER_*` sizes shared skcipher descriptors.
- `KEYMOD` is the fixed key modifier string used by protected blob decapsulation descriptors.
- The constructor prototypes accept caller-owned `u32 *desc` buffers, `struct alginfo` key/algorithm descriptors, sizes such as `ivsize` and `icvsize`, mode flags such as `is_qi`, `geniv`, and `is_rfc3686`, SEC era, and DMA addresses for job/protected-key descriptors.

The header intentionally does not define `struct alginfo`; it relies on callers already including the CAAM descriptor-construction type definitions.

## Control flow and usage

Callers typically use this header in three steps:

1. Choose an algorithm entry and compute key/auth/IV attributes.
2. Use the `DESC_*` size macros with `desc_inline_query()` or fixed buffer sizing to decide whether keys can be embedded inline while keeping job plus shared descriptors within CAAM descriptor limits.
3. Populate `struct alginfo` and call a constructor to write the final descriptor words into per-transform buffers.

For QI users, the `DESC_QI_*` macros add the extra descriptor words needed to consume QI frame metadata such as assoclen and IV. For RFC3686 authenc, callers add `DESC_AEAD_CTR_RFC3686_LEN` to the base descriptor estimate because nonce/counter setup is not included in the base AEAD macro.

## State and persistence behavior

The header has no runtime state. Its constants become compile-time sizing rules and its prototypes define how C modules share descriptor-building behavior. The `KEYMOD` string is compiled into protected blob descriptors through `cnstr_desc_protected_blob_decap()`.

## Dependencies and integration points

This header depends on CAAM command sizing (`CAAM_CMD_SZ`), CAAM/DMA types (`u32`, `dma_addr_t`), and `struct alginfo`, all supplied by surrounding CAAM kernel headers. It is included by `caamalg_desc.c` and by algorithm frontends such as `caamalg_qi.c`. Its exported API is internal to the CAAM driver/module but uses `EXPORT_SYMBOL` implementations so multiple compilation units can link to the constructor functions.

The macros directly influence `DESC_MAX_USED_BYTES` and descriptor inline-key decisions in QI code. If the estimates are too small, the driver may overrun the hardware descriptor buffer or incorrectly inline key material; if too large, it may unnecessarily fall back to DMA key loads.

## Risks and edge cases

- Descriptor length macros must track exact constructor growth. Any new command in `caamalg_desc.c` should be reflected here or callers can under-allocate buffers.
- QI and non-QI variants are separated by macro name, so callers must choose the variant matching the constructor's `is_qi` flag.
- `DESC_AEAD_CTR_RFC3686_LEN` has a note that the nonce is counted in `cdata.keylen`; callers must coordinate key layout and sizing.
- `KEYMOD` is a protocol input for protected blobs. Changing it would break compatibility with blob decapsulation semantics.
- The header declares constructors for features not necessarily registered by every frontend; hardware capability checks remain the caller's responsibility.

## Test signals

Compile-time coverage should catch missing declarations and type mismatches. Runtime tests should verify descriptor construction for maximum-size keys, QI inline-key boundary cases, RFC3686 key-plus-nonce lengths, and every `DESC_*` length used in `desc_inline_query()`. A useful regression signal is that CAAM crypto algorithm registration succeeds and kernel crypto self-tests do not report descriptor length or invalid command failures across supported SEC eras.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi.c -->
