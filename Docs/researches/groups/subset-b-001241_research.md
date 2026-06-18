# subset-b-001241 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_skcipher.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_skcipher.c

### Purpose
This file implements the RK3288 crypto engine skcipher algorithms for AES, DES, and 3DES in ECB and CBC modes. It is the symmetric-cipher request layer for the Rockchip crypto driver: it validates request shape, routes unsupported requests to a software fallback, programs hardware registers, drives block DMA, maintains CBC IV semantics across scatterlist segments, and registers `skcipher_engine_alg` instances through shared `rk_crypto_tmp` descriptors declared in the Rockchip crypto core.

### Important APIs, types, and functions
The exported objects are `rk_ecb_aes_alg`, `rk_cbc_aes_alg`, `rk_ecb_des_alg`, `rk_cbc_des_alg`, `rk_ecb_des3_ede_alg`, and `rk_cbc_des3_ede_alg`. Their `base` members expose Linux Crypto API names such as `ecb(aes)`, `cbc(aes)`, `ecb(des)`, and `cbc(des3_ede)`, while their engine operation points to `rk_cipher_run()`.

Key setup is handled by `rk_aes_setkey()`, `rk_des_setkey()`, and `rk_tdes_setkey()`. AES accepts 128, 192, and 256 bit keys, DES uses `verify_skcipher_des_key()`, and 3DES uses `verify_skcipher_des3_key()`. Each setter stores the hardware key in `struct rk_cipher_ctx` and forwards the key to `ctx->fallback_tfm`.

Request entry points such as `rk_aes_cbc_encrypt()`, `rk_des3_ede_cbc_decrypt()`, and the ECB variants only set `struct rk_cipher_rctx::mode`, including `RK_CRYPTO_DEC` for decrypt, then call `rk_cipher_handle_req()`. `rk_cipher_tfm_init()` allocates a fallback skcipher with `CRYPTO_ALG_NEED_FALLBACK` and expands request size to include both `struct rk_cipher_rctx` and fallback request storage. `rk_cipher_tfm_exit()` wipes the key and frees the fallback.

### Control flow
`rk_cipher_handle_req()` first calls `rk_cipher_need_fallback()`. Hardware is bypassed for empty requests, unaligned source or destination offsets, segment lengths not divisible by the cipher block size, or source/destination scatterlists whose corresponding segment lengths differ. Counters such as `stat_fb_align`, `stat_fb_len`, `stat_fb_sgdiff`, and `stat_fb` are updated on fallback paths.

Hardware requests are sent to the device-wide `crypto_engine` from `get_rk_crypto()`. `rk_cipher_run()` is the engine callback. It resumes runtime PM, records request statistics, snapshots CBC decrypt IV material, and then iterates over matching source/destination scatterlist entries. Each segment is DMA-mapped, `rk_cipher_hw_init()` programs AES or TDES control/key/IV/byteswap registers, `crypto_dma_start()` writes BRDMA/BTDMA addresses and starts the block, and the code waits up to two seconds for `rkc->complete`. On success it unmaps DMA and advances the IV for the next scatterlist entry. On timeout it reports `-EFAULT`; on DMA mapping errors it returns `-EINVAL`.

### State and persistence behavior
Persistent transform state is the raw key, key length, and fallback transform in `struct rk_cipher_ctx`. Per-request state is the hardware mode, device pointer, backup IV, and fallback request storage in `struct rk_cipher_rctx`. Device state lives in `struct rk_crypto_info`: MMIO base, completion, status, request counters, runtime PM device, and crypto engine. No disk persistence exists. Sensitive key material is zeroed on transform exit and decrypt backup IVs are wiped after use.

### Dependencies and integration points
This file depends on the Linux Crypto API skcipher and crypto engine layers, DMA mapping, runtime PM, scatterwalk helpers, DES key verification helpers, and Rockchip-local register definitions from `rk3288_crypto.h`. Integration with the platform driver occurs through `get_rk_crypto()`, the shared engine, IRQ completion state, and registration of the `rk_crypto_tmp` templates elsewhere in the Rockchip driver.

### Risks
The fast path requires tightly paired scatterlists; otherwise fallback is frequent. `rk_cipher_need_fallback()` walks source and destination together but does not explicitly verify that the remaining total length is covered if one list ends early, so tests should cover malformed or short SG chains. Error handling after mapping failures has subtle labels: the path after a destination map failure unmaps source via `theend_sgs`, while the in-place path should avoid double-unmap assumptions. The two-second blocking wait in the engine worker makes interrupt delivery and status setting critical. IV handling across multi-entry CBC decrypt depends on backing up the last ciphertext block before overwrite.

### Test signals
Useful signals include Crypto API selftests for AES/DES/3DES ECB and CBC with 128/192/256 bit AES keys, weak DES/3DES key rejection, zero-length behavior, unaligned offsets, mismatched source/destination SG segment sizes, in-place versus out-of-place operation, multi-segment CBC IV propagation, runtime PM resume failures, DMA map failures, and forced IRQ timeout. Fallback counters should increase for alignment and length cases, while hardware request counters should increase only for aligned block-sized requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_skcipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/s5p-sss.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/s5p-sss.c

### Purpose
This file is the Samsung S5PV210/Exynos Security SubSystem driver for AES skcipher acceleration and, on supported Exynos variants with `CONFIG_CRYPTO_DEV_EXYNOS_HASH`, MD5/SHA1/SHA256 ahash acceleration. It owns MMIO register definitions, platform variant data, Crypto API algorithm registration, request queues, interrupt handling, DMA scatterlist management, and hash buffering for partial blocks.

### Important APIs, types, and functions
`struct samsung_aes_variant` selects AES/HASH register offsets and clock names for `samsung,s5pv210-secss`, `samsung,exynos4210-secss`, and `samsung,exynos5433-slim-sss`. `struct s5p_aes_dev` is the device singleton and contains clocks, MMIO bases, IRQ, current skcipher request, mapped SG state, copy SGs for unaligned data, AES queue/tasklet, optional hash queue/tasklet, hash flags, and the transfer buffer. `struct s5p_aes_ctx` stores the AES key and device pointer per transform. `struct s5p_hash_reqctx` stores per-request hash state: digest context, buffered tail, SG copy/allocation state, processed byte count, final/update mode, and error state. `struct s5p_hash_ctx` stores the selected hash flags, device pointer, and shash fallback.

The AES algorithms in `algs[]` register `ecb(aes)`, `cbc(aes)`, and `ctr(aes)`. Hash algorithms in `algs_sha1_md5_sha256[]` register `sha1`, `md5`, and `sha256` when hash support is enabled. Core AES functions include `s5p_aes_setkey()`, `s5p_aes_crypt()`, `s5p_aes_handle_req()`, `s5p_tasklet_cb()`, `s5p_aes_crypt_start()`, and `s5p_aes_interrupt()`. Core hash functions include `s5p_hash_init()`, `s5p_hash_update()`, `s5p_hash_final()`, `s5p_hash_finup()`, `s5p_hash_prepare_request()`, `s5p_hash_xmit_dma()`, `s5p_hash_handle_queue()`, and `s5p_hash_tasklet_cb()`.

### Control flow
AES callers set a request mode through wrappers such as `s5p_aes_cbc_encrypt()` or `s5p_aes_ctr_crypt()`. `s5p_aes_crypt()` rejects zero-length no-ops and non-block-sized ECB/CBC requests, stores mode in `s5p_aes_reqctx`, and enqueues the request. `s5p_tasklet_cb()` dequeues one request from the one-entry crypto queue, sets `dev->req` and `dev->ctx`, then calls `s5p_aes_crypt_start()`. That function programs AES mode, key size, byte swapping, IV or counter registers, maps/copies input and output SGs as needed, starts BRDMA/BTDMA by writing address and length registers, and enables DMA interrupts. `s5p_aes_interrupt()` advances SG entries on DMA interrupts, clears pending bits, copies back unaligned destination buffers at the end, updates CBC/CTR IV from hardware registers, completes the request, and schedules the tasklet for more queued work.

Hash control flow is separate. `s5p_hash_update()` buffers small input until it exceeds one block. `s5p_hash_final()` uses the shash fallback if no hardware data was processed and the buffered message is shorter than one block; otherwise it enqueues a final operation. `s5p_hash_prepare_request()` combines buffered bytes with the current request, keeps a final partial block for later update calls, and constructs either a direct SG, an allocated SG list, or a copied contiguous SG buffer depending on alignment and list shape. `s5p_hash_xmit_dma()` maps the SG and starts HASH DMA. The shared IRQ handler notices HASH DMA, partial, and done interrupts; the hash tasklet unmaps DMA, reads digest registers, completes requests, and drains the hash queue.

### State and persistence behavior
The driver is effectively singleton via static `s5p_dev`; probe rejects a second device. Persistent runtime state is in `s5p_aes_dev`, including current request pointers and queues. AES transform state persists keys for the transform lifetime. Hash request export/import copies `struct s5p_hash_reqctx` plus buffered bytes, enabling Crypto API state migration for partial hashes. No on-disk persistence exists. Unaligned AES copies allocate pages and are freed in `s5p_sg_done()`. Hash SG copies are freed in `s5p_hash_finish_req()`. AES keys are not explicitly zeroed on transform teardown in this file.

### Dependencies and integration points
The file integrates with platform devices through OF match data, `devm_ioremap_resource()`, clocks, a threaded feed-control IRQ, tasklets, Linux DMA mapping, and the Crypto API skcipher/ahash registration APIs. It relies on Samsung SSS register layouts and optional Kconfig coverage for Exynos hash. The hash and AES paths share feed-control interrupt status registers and FIFO routing, so interrupt sequencing is a central integration point.

### Risks
Global singleton `s5p_dev` limits multi-device systems and makes transform contexts depend on probe/remove ordering. AES uses `GFP_ATOMIC` page allocation for unaligned SG copies; allocation failure aborts requests. Hash buffer and SG preparation logic is complex and sensitive to off-by-one errors around block boundaries, `skip`, `hash_later`, and final/update overlap. The probe path mutates `res->end` to extend the mapping for hash registers and rolls it back on fallback, which is fragile if resource objects are shared or inspected elsewhere. Hash fallback is only for small final messages, not a general fallback for all hardware failures.

### Test signals
Exercise AES ECB/CBC/CTR with 128/192/256 bit keys, zero-length requests, ECB/CBC non-block-aligned rejection, CTR partial-block acceptance, in-place and out-of-place SGs, unaligned SG lengths that trigger copy buffers, multi-entry SG interrupt advancement, and IV/counter update after completion. Hash tests should cover MD5/SHA1/SHA256 digest/update/final/finup, messages of length 0, 1, 63, 64, 65, multi-block, exported/imported state, unaligned SG lists, copied SG cleanup, queue backlog behavior, and the optional hash-disabled probe path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/s5p-sss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/sa2ul.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/sa2ul.c

### Purpose
This file implements the Texas Instruments K3 SA2UL/SA3UL crypto accelerator driver. It supports skcipher AES-CBC, AES-ECB, 3DES-CBC, 3DES-ECB, ahash SHA1/SHA256/SHA512, and authenc HMAC-SHA1/HMAC-SHA256 with AES-CBC AEAD, with supported algorithms gated by SoC match data. The driver builds SA security contexts, command labels, DMA metadata, and scatterlist mappings used by the accelerator packet interface.

### Important APIs, types, and functions
The main algorithm table is `sa_algs[]`, whose entries are selected by `enum sa_algo_id` and registered by `sa_register_algos()`. SoC capability is expressed by `struct sa_match_data` instances `am654_match_data` and `am64_match_data`; OF compatibles include `ti,j721e-sa2ul`, `ti,am654-sa2ul`, `ti,am64-sa2ul`, and `ti,am62-sa3ul`.

Security context setup flows through `sa_init_ctx_info()`, `sa_init_sc()`, `sa_set_sc_enc()`, `sa_set_sc_auth()`, `sa_set_swinfo()`, and `sa_format_cmdl_gen()`. `sa_update_cmdl()` patches per-request lengths, offsets, IVs, and auth information into command-label templates. `sa_run()` is the common DMA submission path for skcipher, ahash digest, and AEAD. Algorithm-facing entry points include `sa_cipher_cra_init()`, `sa_cipher_setkey()`, `sa_cipher_run()`, `sa_sha_cra_init_alg()`, `sa_sha_run()`, `sa_aead_setkey()`, and `sa_aead_run()`.

### Control flow
Probe allocates `struct sa_crypto_data`, maps registers, enables runtime PM, creates a DMA pool for security contexts, requests `rx1`, `rx2`, and `tx` DMA channels, configures slave widths, enables SA engine bits, registers supported algorithms, populates child devices, and adds device links.

For skcipher transforms, init allocates encryption and decryption security contexts plus a software fallback. Setkey validates key size, configures mode-control instruction arrays for AES or 3DES, sets inverse-key behavior where needed, builds encrypt/decrypt security contexts, and formats command label templates. Request execution rejects empty input as success, rejects non-block-aligned lengths, and falls back for sizes over `SA_MAX_DATA_SZ` or within the documented unsafe 240..255 byte range. Hardware requests fill `struct sa_req` and call `sa_run()`.

`sa_run()` allocates `struct sa_rx_data`, chooses `rx1` for packets below 256 bytes and `rx2` otherwise, copies the command label template, updates it for the request, maps source and destination SGs with `dma_map_sgtable()`, uses `sg_split()` when the operation length needs a bounded SG view, prepares RX and TX DMA descriptors, writes SA metadata via `dmaengine_desc_get_metadata_ptr()`, submits RX before TX, and returns `-EINPROGRESS`. Completion callbacks sync DMA, update IV/tag/digest material, free split/mapped SG state, and complete the Crypto API request.

Hash digest requests use hardware only for one-shot `digest()` in `sa_sha_run()`; incremental `init/update/final/finup/export/import` delegate to the fallback ahash. Zero-length hashes copy kernel zero-message constants. AEAD parses authenc keys, prepares HMAC ipad/opad via shash helpers, builds combined auth/encrypt contexts, and compares or appends tags in `sa_aead_dma_in_callback()`.

### State and persistence behavior
Per-device state in `struct sa_crypto_data` includes the MMIO base, DMA pool, three DMA channels, SoC match data, runtime PM device, and security-context ID bitmap guarded by `scid_lock`. Per-transform `struct sa_tfm_ctx` owns encryption, decryption, and auth `struct sa_ctx_info`, fallback transforms, key storage, shash handle, and auth key. Per-request state is stack `struct sa_req` plus heap `struct sa_rx_data` for asynchronous completion. No persistent storage exists. Security context memory is DMA-pool allocated and explicitly freed; context buffers are cleared before reuse.

### Dependencies and integration points
The driver depends on Linux DMAengine metadata support, DMA pools, scatterlist splitting, runtime PM, OF platform population, `crypto_authenc_extractkeys()`, shash/ahash/skcipher/aead Crypto API helpers, and register/packet contracts from `sa2ul.h`. It integrates with K3 UDMA-style channels named `rx1`, `rx2`, and `tx`, and with child platform devices under the SA node.

### Risks
The hardware has a documented unsafe packet-size window from 240 to 255 bytes and a max request size of 64 KiB; fallback coverage for these boundaries is critical. DMA cleanup is subtle because `sa_run()` can use original SGs, static single-entry SGs, or `sg_split()` allocations. Several init error paths allocate fallback transforms or context IDs before later failure and should be checked for leaks. Authentication tag comparison uses `memcmp()` rather than a constant-time helper. In this source snapshot, `struct sa_cmdl_upd_info` in `sa2ul.h` declares `aux_key_info` twice; that would normally be a compile-time error and should be reconciled against the intended upstream header.

### Test signals
Run Crypto API manager tests for all registered algorithms on each supported SoC capability mask. Cover packet lengths 0, 1 block, 239, 240, 255, 256, 257, 65535, and 65536+, with fallback assertions for unsafe/oversize cases. Test AES key sizes, 3DES key validation, authenc key parsing, AEAD encrypt/decrypt and bad-tag `-EBADMSG`, SHA zero-message constants, SHA digest versus incremental fallback behavior, in-place and split SGs, RX channel selection around 256 bytes, DMA mapping failures, probe deferral for channels, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/sa2ul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/sa2ul.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/sa2ul.h

### Purpose
This header defines the SA2UL driver contract shared by `sa2ul.c`: register offsets, engine-enable bits, command label layout, security-context sizes and offsets, request subtype encoding, data-size limits, core device/transform/request structures, and algorithm ID enumerations. It is the hardware protocol map for the TI K3 SA2UL packet accelerator.

### Important APIs, types, and definitions
Key register definitions include `SA_ENGINE_STATUS` and `SA_ENGINE_ENABLE_CONTROL`, with enable bits for encryption, authentication, TRNG, PKA, context cache, and CPPI ports. Command label offsets such as `SA_CMDL_OFFSET_NESC`, `SA_CMDL_OFFSET_DATA_LEN`, and `SA_CMDL_OFFSET_OPTION_CTRL1` define the bytes patched into DMA metadata. `SA_MAX_DATA_SZ` caps hardware packets at `U16_MAX`, while `SA_UNSAFE_DATA_SZ_MIN` and `SA_UNSAFE_DATA_SZ_MAX` document the 240..255 byte fallback range.

`struct sa_crypto_data` holds per-device MMIO, match data, DMA pool, context ID bitmap, and RX/TX DMA channels. `struct sa_cmdl_param_info` and `struct sa_cmdl_upd_info` describe positions within command labels that are updated per request. `struct sa_ctx_info` owns one DMA security context, its physical address, command label template, update metadata, and EPIB words. `struct sa_tfm_ctx` aggregates encryption, decryption, and auth contexts plus fallback transforms. `struct sa_sha_req_ctx` embeds ahash fallback request storage. Enumerations `sa_ealg_id`, `sa_aalg_id`, and `sa_eng_algo_id` encode algorithm selection for security contexts and mode-control instruction tables.

### Control flow and state model
The header itself has no executable control flow, but it shapes all runtime behavior in `sa2ul.c`. Transform init allocates `sa_ctx_info` entries described here; setkey fills security context offsets such as `SA_CTX_ENC_KEY_OFFSET`; request execution patches fields described by `sa_cmdl_upd_info`; DMA callbacks decode request subtype fields such as `SA_REQ_SUBTYPE_ENC` and `SA_REQ_SUBTYPE_DEC`.

### Dependencies and integration points
The header depends on Crypto API AES/SHA constants and Linux bit/align conventions. It is included directly by `sa2ul.c` and indirectly constrains device tree matched hardware because DMA channel selection, context sizes, and engine IDs must match SA2UL firmware/hardware expectations.

### Risks
The definitions are protocol-sensitive: incorrect offsets or sizes corrupt command labels or security contexts. The duplicate `aux_key_info` field in `struct sa_cmdl_upd_info` in this snapshot is a direct compile risk. The `SA_MAX_NUM_CTX` bitmap and context ID macros must stay consistent with hardware limits. Unsafe-size constants are security and correctness relevant because the C file relies on them to avoid unpredictable hardware output.

### Test signals
Compile coverage is essential for this header. Runtime tests should validate context allocation up to `SA_MAX_NUM_CTX`, command label sizes never exceeding `SA_MAX_CMDL_WORDS`, fallback at unsafe sizes, correct IV indexes for AES-CBC and 3DES-CBC, and algorithm registration only for capabilities advertised by match data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/sa2ul.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/sahara.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/sahara.c

### Purpose
This file implements the Freescale/NXP SAHARA2 crypto accelerator driver for i.MX27/i.MX53-era hardware. It registers AES ECB/CBC skcipher acceleration and SHA1/SHA256 ahash acceleration depending on hardware version, builds SAHARA hardware descriptors and link tables, handles interrupts, and uses the Linux crypto engine to serialize requests.

### Important APIs, types, and functions
`struct sahara_hw_desc` and `struct sahara_hw_link` describe the hardware descriptor rings. `struct sahara_ctx` stores AES key material and fallback skcipher. `struct sahara_aes_reqctx` stores mode, decrypt IV backup, and fallback request storage. `struct sahara_sha_reqctx` stores buffered hash bytes, saved hardware context, mode flags, digest sizes, SG chains, total length, and first/last flags. `struct sahara_dev` owns MMIO, clocks, completion, coherent descriptor/key/IV/context/link buffers, current SG state, and the crypto engine.

AES registration is in `aes_algs[]`, SHA1 in `sha_v3_algs[]`, and SHA256 in `sha_v4_algs[]` for versions above 3. Request execution is centralized by `sahara_do_one_request()`. AES uses `sahara_aes_setkey()`, `sahara_aes_crypt()`, `sahara_hw_descriptor_create()`, and `sahara_aes_process()`. Hashing uses `sahara_sha_init()`, `sahara_sha_enqueue()`, `sahara_sha_prepare_request()`, descriptor creation helpers, and `sahara_sha_process()`.

### Control flow
Probe maps MMIO, requests IRQ, enables `ipg` and `ahb` clocks, allocates coherent descriptors, key/IV buffers, context buffer, and link table, starts a crypto engine, verifies hardware version against compatible strings, resets hardware into batch mode, enables interrupts, and registers algorithms.

AES setkey accepts only AES-128 in hardware; AES-192 and AES-256 are configured on the fallback transform. AES crypt rejects zero-length as no-op, falls back when key length is not 128 bits, rejects non-block-aligned requests, stores mode, and transfers the request to the engine. The engine callback assigns the request to global device fields, copies IV for CBC, builds a key descriptor followed by a data-link descriptor, maps source and destination SGs, writes descriptor address to `SAHARA_REG_DAR`, waits up to one second for IRQ completion, unmaps DMA, updates CBC IV, and finalizes the request.

Hash update/final calls enqueue ahash requests to the same crypto engine. `sahara_sha_prepare_request()` buffers insufficient data until a block can be processed, carries trailing partial blocks across updates, and builds chained SGs when buffered bytes precede request SG data. The first hash operation uses a mode/init descriptor; later operations load the saved context then hash more data. Completion copies the hardware context back and, on the last request, copies the digest to `req->result`.

### State and persistence behavior
`dev_ptr` is a singleton pointer used by transform and request paths. Coherent memory for descriptors, links, key/IV, and hash context persists for the device lifetime. Transform state persists AES key length/key and fallback. Request state persists hash context through export/import by copying `struct sahara_sha_reqctx`. There is no disk persistence. The driver does not explicitly zero AES key buffers on exit.

### Dependencies and integration points
The file integrates with platform OF compatibles `fsl,imx53-sahara` and `fsl,imx27-sahara`, Linux clocks, IRQ, DMA mapping, coherent DMA allocation, scatterwalk, and the crypto engine registration helpers. Hardware completion depends on `sahara_irq_handler()` clearing interrupt/error bits and completing `dma_completion`.

### Risks
Hardware AES supports only AES-128, so fallback correctness for AES-192/256 is required. Descriptor link capacity is fixed at 20 links; high-fragmentation SGs fail. `dev_ptr` implies a singleton and can be fragile around multiple devices. The remove path calls `crypto_engine_exit()` before unregistering algorithms, while probe failure unregister order should be checked against engine users. Hash processing mutates `req->nbytes` in final and depends on copied context sizes. Timeout handling returns errors after DMA unmap, but hardware reset/recovery after timeout is limited.

### Test signals
Test AES ECB/CBC AES-128 hardware, AES-192/256 fallback, CBC IV update for encrypt and decrypt, non-block-aligned rejection, SG lists near and beyond 20 links, in-place and out-of-place requests, IRQ timeout injection, and probe version mismatch. Hash tests should cover SHA1 on v3/v4, SHA256 only on v4, update/final/finup/digest, messages shorter than a block, exact-block messages, multi-update context carry, export/import, and timeout/error IRQ decoding paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/sahara.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/crypto/starfive/Kconfig

### Purpose
This Kconfig file defines `CRYPTO_DEV_JH7110`, the build option for the StarFive JH7110 cryptographic engine driver. It gates compilation of the StarFive crypto module and declares the Crypto API algorithm dependencies needed by the AES, hash, and RSA implementation files.

### Important configuration behavior
`CRYPTO_DEV_JH7110` is a tristate option named "StarFive JH7110 cryptographic engine driver". It depends on either `SOC_STARFIVE && AMBA_PL08X` or `COMPILE_TEST`, and also on `HAS_DMA`. It selects `CRYPTO_ENGINE`, HMAC, SHA256, SHA512, SM3, RSA, AES, CCM, GCM, ECB, CBC, and CTR support. The help text states that the module accelerates public key algorithms, skciphers, AEAD, and hash functions, and that the module name is `jh7110-crypto`.

### Integration points
The selected symbols align with the source files listed in the local Makefile: `jh7110-cryp.o` for the platform/engine, `jh7110-hash.o` for hash/HMAC/SM3/SHA, `jh7110-rsa.o` for RSA, and `jh7110-aes.o` for AES skcipher/AEAD. The `AMBA_PL08X` dependency reflects the DMA controller expected by the driver.

### Risks
Because the option selects several crypto algorithms, enabling it can pull in more Crypto API code than only the hardware driver. `COMPILE_TEST` permits builds outside StarFive SoCs, so compile coverage should catch missing architecture assumptions. Runtime still requires DMA channels, clocks, reset, and a matching device tree node.

### Test signals
Build-test as built-in and module, with and without `COMPILE_TEST`, and verify that selecting the option brings in the required crypto helpers. Runtime tests should confirm that the module registers only when the `starfive,jh7110-crypto` platform device and DMA resources are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/Makefile -->
## sources/distributed-fs/ceph-client/drivers/crypto/starfive/Makefile

### Purpose
This Makefile wires the StarFive JH7110 crypto driver objects into the kernel build. It builds one module or built-in object named `jh7110-crypto` when `CONFIG_CRYPTO_DEV_JH7110` is enabled.

### Important build behavior
`obj-$(CONFIG_CRYPTO_DEV_JH7110) += jh7110-crypto.o` declares the composite target. `jh7110-crypto-objs := jh7110-cryp.o jh7110-hash.o jh7110-rsa.o jh7110-aes.o` links the platform driver, hash implementation, RSA implementation, and AES implementation into that composite target.

### Integration points
The object list must stay aligned with prototypes in `jh7110-cryp.h`: `starfive_aes_register_algs()`, `starfive_hash_register_algs()`, and `starfive_rsa_register_algs()` are called from `jh7110-cryp.c`, so missing objects would break linking.

### Risks
Any new algorithm file needs to be added here and to the platform registration/unregistration sequence. Object ordering is relevant because the final module contains cross-object references, although normal kbuild resolves them within the composite object.

### Test signals
Build `CONFIG_CRYPTO_DEV_JH7110=m` and `=y`, confirm the resulting module name is `jh7110-crypto`, and check that all register/unregister symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-aes.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-aes.c

### Purpose
This file implements AES acceleration for the StarFive JH7110 crypto engine. It registers AES ECB/CBC/CTR skcipher algorithms and AES GCM/CCM AEAD algorithms, manages fallback transforms for unsupported request shapes, programs AES registers, moves payload through DMA, handles AAD/tag processing for AEAD, and finalizes requests through the shared crypto engine.

### Important APIs, types, and functions
The file uses shared `struct starfive_cryp_ctx`, `struct starfive_cryp_dev`, and `struct starfive_cryp_request_ctx` from `jh7110-cryp.h`. Register offsets cover AES key, IV, nonce, AAD length, message length, IV length, FIFO, and CSR fields. `FLG_MODE_MASK` and `FLG_ENCRYPT` encode request mode in `cryp->flags`.

Hardware setup functions include `starfive_aes_wait_busy()`, `starfive_aes_wait_keydone()`, `starfive_aes_wait_gcmdone()`, `starfive_aes_write_key()`, `starfive_aes_write_iv()`, `starfive_aes_ccm_init()`, and `starfive_aes_hw_init()`. DMA is configured through `starfive_aes_dma_init()`, `starfive_aes_dma_xfer()`, and `starfive_aes_map_sg()`. Engine callbacks are `starfive_aes_do_one_req()` for skcipher and `starfive_aes_aead_do_one_req()` for AEAD. Registration is via `starfive_aes_register_algs()` and `starfive_aes_unregister_algs()`.

### Control flow
Transform init finds a device with `starfive_cryp_find_dev()`, allocates a software fallback such as `ecb(aes-lib)`, `cbc(aes-lib)`, `ctr(aes-lib)`, `gcm_base(ctr(aes-lib),ghash-lib)`, or `ccm_base(ctr(aes-lib),cbcmac-aes-lib)`, and sizes request context to include fallback storage. Setkey validates AES key length, stores the key, and forwards it to the fallback.

Skey cipher wrappers set mode and encryption flags, reject non-block-aligned ECB/CBC lengths, run `starfive_aes_check_unaligned()`, and either fallback or enqueue to the crypto engine. The engine callback stores request pointers and lengths in `cryp`, initializes hardware, sets up DMA, maps SGs one segment at a time, handles split source/destination progression with `scatterwalk_ffwd()`, and finalizes the skcipher request. Completion reads updated IV for CBC/CTR.

AEAD wrappers additionally validate CCM IV format and always fallback for CCM decrypt because this hardware path cannot verify non-aligned CCM text. AEAD engine execution skips associated data using `scatterwalk_ffwd()`, copies incoming tags for decrypt, pads text with `sg_zero_buffer()` when needed, initializes hardware lengths, writes AAD through GCM nonce registers or CCM data FIFO, transfers payload by DMA, reads or verifies the authentication tag, and finalizes the AEAD request.

### State and persistence behavior
Per-device state in `starfive_cryp_dev` is reused for the active request: request pointer union, `assoclen`, `total_in`, `total_out`, tag buffers, auth size, flags, error, DMA completion, DMA configs, and side-channel mitigation flag. Per-transform state holds key bytes, key length, fallback transforms, and cached device pointer. Per-request context stores CSR images, SG pointers, total lengths, digest metadata shared with other algorithm files, and temporary AAD buffer pointer. No disk persistence exists. Fallback transforms are freed on transform exit; AAD buffers are allocated per AEAD request and freed before payload transfer.

### Dependencies and integration points
This file depends on the shared platform driver in `jh7110-cryp.c` for clocks, reset, DMA channels, engine allocation, and algorithm registration. It uses Linux DMAengine, crypto engine, scatterwalk, AEAD/skcipher internals, `crypto_gcm_check_authsize()`, and register definitions from `jh7110-cryp.h`.

### Risks
DMA error handling in `starfive_aes_map_sg()` can return after a destination map failure without unmapping a successfully mapped source in that iteration. The AEAD path uses `sg_dma_len(rctx->in_sg)` before DMA mapping in the `sg_zero_buffer()` length expression, which deserves scrutiny because `sg_dma_len` is normally valid after mapping. Hardware polling timeouts must propagate and leave the engine usable for later requests. AAD handling assumes enough allocated padding and correct CCM formatting. Device state is shared through `cryp->flags` and request unions, so crypto engine serialization is required for correctness.

### Test signals
Run AES ECB/CBC/CTR tests for 128/192/256 bit keys, block and partial CTR lengths, unaligned offset/length fallback, in-place and out-of-place SGs with unequal segment sizes, IV update after CBC/CTR, DMA timeout injection, and side-channel module parameter coverage. AEAD tests should cover GCM auth sizes, CCM auth sizes and IV L field validation, encrypt/decrypt with AAD lengths 0, short, block-sized, and multi-block, bad-tag detection, CCM decrypt fallback, empty plaintext with AAD, and SG padding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-cryp.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-cryp.c

### Purpose
This file is the platform and device-lifetime layer for the StarFive JH7110 crypto engine. It probes the hardware, maps registers, enables clocks and reset, requests DMA channels, creates the shared crypto engine, maintains a global list of devices for algorithm transform init, registers AES/hash/RSA algorithms, and tears everything down on remove.

### Important APIs, types, and functions
`struct starfive_dev_list` wraps the global `dev_list` and a spinlock. `starfive_cryp_find_dev()` is exported to sibling algorithm files and returns the first registered device, caching it in the transform context. `side_chan` is a module parameter that enables AES side-channel mitigation and is copied into `cryp->side_chan` at probe. `starfive_dma_init()` requests `tx` and `rx` DMA channels; `starfive_dma_cleanup()` releases them. `starfive_cryp_probe()` and `starfive_cryp_remove()` own platform lifecycle. The OF match table binds `starfive,jh7110-crypto`.

### Control flow
Probe allocates `struct starfive_cryp_dev`, maps the MMIO resource while recording `phys_base`, sets `dma_maxburst`, reads the side-channel parameter, obtains `hclk`, `ahb`, and shared reset control, enables clocks, deasserts reset, adds the device to the global list, requests DMA channels, allocates and starts a one-slot crypto engine, then registers AES, hash, and RSA algorithms in that order. Failure unwinds registered algorithms, engine, DMA channels, list membership, clocks, and reset.

Remove unregisters AES/hash/RSA algorithms, exits the crypto engine, releases DMA channels, removes the device from the global list, disables clocks, and asserts reset.

### State and persistence behavior
Runtime state is entirely in memory. The global device list persists for the module lifetime and allows transform initialization to find hardware after algorithm registration. Each transform caches a `struct starfive_cryp_dev *` once found. No runtime PM is used here, so clocks remain enabled from probe until remove. The side-channel parameter is read at probe and is not dynamically re-applied to existing devices.

### Dependencies and integration points
This file integrates with Linux platform driver infrastructure, OF matching, reset controller, common clock framework, DMAengine channel lookup, crypto engine, and the sibling StarFive AES/hash/RSA modules through register/unregister function calls declared in `jh7110-cryp.h`.

### Risks
The global list selection returns the first device and does not load-balance across multiple JH7110 crypto engines. Clock enable and reset calls are not fully checked after `clk_prepare_enable()` and `reset_control_deassert()`, so failures there could be missed. Algorithm registration is global; if multiple devices were ever supported, duplicate registration would need handling. The engine has queue length 1, making request serialization simple but limiting concurrency.

### Test signals
Probe tests should cover missing MMIO, missing clocks, missing reset, missing `tx`/`rx` DMA channels, engine allocation failure, and partial algorithm registration failure. Remove tests should verify unregister ordering and resource release. Runtime tests should confirm transform init fails with `-ENODEV` before a device is listed and succeeds after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-cryp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-cryp.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-cryp.h

### Purpose
This header defines the shared register layout, bitfields, limits, device state, transform state, and request state for the StarFive JH7110 crypto driver family. It is included by the platform driver and algorithm implementations for AES, hash, and RSA.

### Important APIs, types, and definitions
Top-level register offsets include `STARFIVE_ALG_CR_OFFSET`, FIFO, interrupt mask/flag, and DMA length registers. AES, hash, and PKA control/status words are represented as bitfield unions: `union starfive_aes_csr`, `union starfive_hash_csr`, `union starfive_pka_cacr`, and `union starfive_pka_casr`. These define mode encodings, busy/done bits, key-done bits, start/reset bits, hash modes for SM3/SHA2, HMAC flags, and PKA operation sizing.

`struct starfive_rsa_key` stores RSA components and bit lengths. `union starfive_alg_cr` controls top-level algorithm start, DMA enables, done, and clear. `struct starfive_cryp_ctx` is per-transform state shared by all algorithm types: device pointer, request context pointer, hash mode, key buffer, HMAC flag, RSA key, and fallback transforms. `struct starfive_cryp_dev` is per-device state: list node, device, clocks, reset, MMIO, physical base, DMA channels/configs, crypto engine, completion, request lengths, tags, auth size, flags, error, side-channel setting, and active request union. `struct starfive_cryp_request_ctx` is per-request state with CSR image, SG pointers, hash/digest metadata, AAD pointer, RSA scratch buffer, and fallback ahash request storage.

The header declares `starfive_cryp_find_dev()` and algorithm registration functions for hash, RSA, and AES.

### Control flow and state model
The platform driver fills `starfive_cryp_dev` at probe. Algorithm transform init stores a pointer in `starfive_cryp_ctx`. During request execution, algorithm files fill `starfive_cryp_request_ctx` and use the `req` union in `starfive_cryp_dev` to remember the active Crypto API request until the crypto engine callback finalizes it.

### Dependencies and integration points
The header depends on Crypto API AES/hash/SHA/SM3 constants, scatterwalk, Linux DMA mapping and DMAengine, interrupts, completions, and reset/clock-managed platform state through included headers. It is the ABI between `jh7110-cryp.c`, `jh7110-aes.c`, and the unlisted hash/RSA files.

### Risks
C bitfield layout for hardware CSRs can be compiler and endian sensitive; the driver writes the union's `u32 v` to MMIO, so target assumptions must match the hardware ABI. Shared request fields in `starfive_cryp_dev` make crypto engine serialization necessary. `MAX_KEY_SIZE` follows `SHA512_BLOCK_SIZE`, so AES, HMAC, and hash users share a broad key buffer. The flexible ahash fallback request at the end of `starfive_cryp_request_ctx` constrains request-size calculations.

### Test signals
Compile tests should cover all included algorithm files together. Runtime tests should validate CSR mode bits written by AES/hash/RSA paths, DMA completion behavior, fallback request sizing, side-channel flag propagation, tag buffers, and active request union use under serialized engine execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-cryp.h -->
