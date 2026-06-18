# Research: subset-b-001240

Grouped research for `subset-b-001240`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.h

Purpose: declares the OMAP AES hardware accelerator register map, mode flags, platform-data contract, request/device contexts, and cross-file entry points used by the OMAP AES skcipher and GCM implementation.

Important APIs and types: register macros derive key, IV, control, data, tag, IRQ, and DMA-mask offsets from `struct omap_aes_pdata`; flags describe encrypt, CBC, CTR, GCM, RFC4106-GCM, copy state, and fast paths. `struct omap_aes_ctx` stores AES key material, RFC4106 nonce, and skcipher fallback; `struct omap_aes_gcm_ctx` adds an expanded AES key; `struct omap_aes_reqctx` stores per-request mode, IV, tag, and fallback request. `struct omap_aes_dev` owns MMIO, crypto engine, queues, DMA channels, scatterlists, copy buffers, counters, and platform quirks.

Control flow and integration: callers set per-request flags, locate a device with `omap_aes_find_dev()`, program control through `omap_aes_write_ctrl()`, and start/stop DMA with `omap_aes_crypt_dma_start()`/`omap_aes_crypt_dma_stop()`. AEAD paths use the GCM-specific setkey, authsize, encrypt/decrypt, DMA callback, and engine request handler prototypes declared here.

State and persistence: transform contexts persist keys and fallback objects; device state persists queue, DMA, MMIO, and copy-state flags across requests. Request state is transient and must keep the fallback request last.

Dependencies: Linux crypto engine, AEAD/skcipher APIs, DMAengine, scatterlists, OMAP platform data, and AES constants.

Risks and test signals: register offsets and bit meanings are SoC-specific; wrong flags can corrupt IV/tag handling or DMA enablement. Test AES CBC/CTR/GCM/RFC4106 vectors, fallback paths, unaligned scatterlists, runtime PM, DMA callbacks, and probe/remove with each compatible platform data set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.c

Purpose: provides shared scatterlist alignment, copy, and cleanup helpers for OMAP crypto drivers whose hardware and DMA paths require aligned, DMA-zone-capable, block-sized buffers.

Important APIs and functions: `omap_crypto_align_sg()` checks an input/output scatterlist against total length, block size, offset alignment, optional DMA-zone requirements, and single-entry requirements. It either leaves the list in place, builds a bounded list copy with `omap_crypto_copy_sg_lists()`, or allocates a contiguous page buffer with `omap_crypto_copy_sgs()`. `omap_crypto_cleanup()` reverses the operation by copying output data back to the original scatterlist when needed and freeing allocated pages or copied SG tables. `omap_crypto_copy_data()` performs page-mapped copyback across SG boundaries.

Control flow: callers clear the relevant device copy flags, request forced copy/list behavior through `OMAP_CRYPTO_*` flags, and pass a shift selecting the in/out/assoc flag lane. Cleanup later decodes those shifted bits and frees only the resources that were actually allocated.

State and persistence: no module-global runtime state. Persistent effects are the caller's mutated SG pointer and copy flags. Allocated buffers live only for one crypto request and must be cleaned up by the caller on all completion/error paths.

Dependencies and integration: used by OMAP DES and AES-style drivers before DMA/PIO submission. Depends on scatterlist helpers, `scatterwalk_map_and_copy()`, `__get_free_pages(GFP_ATOMIC)`, `kmap_atomic()`, and cache flushing for copied output pages.

Risks and test signals: page allocation order is derived from aligned length; mismatched cleanup length/order leaks memory or frees the wrong range. Copyback with offsets is high risk for partial SGs. Test aligned SGs, bad total length, forced-copy, in-place encryption, single-entry forcing, CONFIG_ZONE_DMA systems, and error unwinds after only one side has been copied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.h

Purpose: exposes the small shared OMAP crypto scatterlist-copy contract used by multiple hardware crypto drivers.

Important APIs and definitions: return-like internal status values distinguish `OMAP_CRYPTO_NOT_ALIGNED` from `OMAP_CRYPTO_BAD_DATA_LENGTH`. Device copy state uses `OMAP_CRYPTO_DATA_COPIED` and `OMAP_CRYPTO_SG_COPIED`, masked by `OMAP_CRYPTO_COPY_MASK` and shifted into per-driver flag fields. Caller option flags request input data copy, forced copy, zero padding, and single-entry list behavior. The exported functions are `omap_crypto_align_sg()` and `omap_crypto_cleanup()`.

Control flow and integration: drivers call `omap_crypto_align_sg()` before programming DMA or PIO, passing the current SG pointer by reference and a caller-owned replacement SG. Completion calls `omap_crypto_cleanup()` with the same flag shift and preserved original output SG when copyback is required.

State and persistence: the header defines no state. Its contract is stateful through the caller's shifted flag bits and through mutated SG pointers that must remain valid until cleanup.

Dependencies: Linux scatterlists, bit operations, and the implementation in `omap-crypto.c`.

Risks and test signals: callers must allocate enough inline `new_sg` storage when forcing a single entry and must keep flag shifts disjoint. Test signals are successful OMAP AES/DES operations with unaligned offsets, short final lengths, in-place requests, and cleanup on failures between input and output alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-des.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-des.c

Purpose: implements OMAP DES and 3DES ECB/CBC hardware acceleration as asynchronous skcipher algorithms backed by DMA when available and by IRQ-driven PIO otherwise.

Important APIs and functions: `omap_des_setkey()` and `omap_des3_setkey()` validate DES/3DES keys and store little-endian key words. `omap_des_crypt()` validates block-aligned request length, sets request mode flags, and enqueues through the crypto engine. `omap_des_crypt_req()` chooses a device, prepares SGs with `omap_crypto_align_sg()`, programs keys/IV/control via `omap_des_write_ctrl()`, and starts DMA/PIO. `omap_des_done_task()` handles DMA unmap/stop, copy cleanup, CBC IV readback, and request finalization.

Control flow: probe maps registers, enables runtime PM, reads hardware revision, requests DMA channels, optionally falls back to IRQ PIO, adds the device to a global list, starts a one-slot crypto engine, and registers four skcipher algorithms. DMA submission maps source/destination SGs, configures both slave channels to the DES data register, starts the hardware trigger, and completes from the TX callback. PIO alternates DATA_IN and DATA_OUT IRQs per block.

State and persistence: global `dev_list` and `list_lock` select the first available device and cache it in `struct omap_des_ctx`. Device state carries active request, copy buffers, DMA channels, runtime PM flags, and counters. Transform contexts persist key material and cached device pointer.

Dependencies and integration: Linux platform driver/OF match `ti,omap4-des`, DMAengine channels `rx`/`tx`, crypto engine skcipher registration, runtime PM, OMAP common SG helpers, and DES key verification helpers.

Risks and test signals: `ctx->dd` caching can bind transforms to a removed device unless lifecycle ordering is correct. In-place requests force input copy, so cleanup must run on every path. PIO path uses `BUG_ON()` for SG state assumptions. Test DES/3DES ECB/CBC known vectors, DMA and no-DMA probe, unaligned SGs, in-place requests, runtime suspend/resume, removal while idle, and DMA error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-des.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-sham.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-sham.c

Purpose: implements OMAP SHA/MD5 hardware hashing and HMAC acceleration for OMAP2/3/4/5, with async ahash algorithms, CPU or DMA transmit paths, runtime PM, sysfs tuning, and software fallback for small or unsupported cases.

Important APIs and functions: ahash methods include `omap_sham_init()`, `omap_sham_update()`, `omap_sham_final()`, `omap_sham_finup()`, `omap_sham_digest()`, `omap_sham_export()`, and `omap_sham_import()`. `omap_sham_prepare_request()` merges buffered bytes with new SG data, selects full blocks, holds back later bytes, and builds aligned/copied SGs. `omap_sham_xmit_cpu()` writes blocks through DIN registers while polling readiness; `omap_sham_xmit_dma()` maps SGs and starts DMA. `omap_sham_finish_req()` releases copied SGs, copies digest state, handles huge-request requeue, runtime PM, and crypto-engine completion. `omap_sham_setkey()` prepares HMAC ipad/opad or hardware auto-XOR state.

Control flow: requests buffer small data until enough bytes exist or final is called. Hardware processing is run through a crypto engine. OMAP2-style control uses `SHA_REG_CTRL`; OMAP4/5 use MODE/LENGTH and optional HMAC key processing. Interrupts and DMA callbacks both queue `done_task`, which waits until output and DMA-ready state agree.

State and persistence: `struct omap_sham_reqctx` persists partial digest, byte count, buffered data, SG walk state, operation, and flags across update/final/export/import. Transform context stores fallback shash and HMAC base shash. Global `sham.dev_list` rotates devices and global flags advertise platform features such as auto-XOR.

Dependencies and integration: crypto engine ahash APIs, DMAengine, scatterwalk, runtime PM, OF/platform resources, sysfs attributes `fallback` and `queue_len`, and software shash fallbacks.

Risks and test signals: final-block logic, huge-request requeue, HMAC auto-XOR versus software ipad/opad, and copied SG cleanup are high risk. `omap_sham_copy_sg_lists()` offset bookkeeping is subtle. Test MD5/SHA1/SHA224/SHA256/SHA384/SHA512 and HMAC vectors, update/final streaming, import/export, zero/small buffers, fallback threshold changes, DMA-disabled polling, OMAP2 big-endian SHA1, OMAP4/5 register layouts, and runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-sham.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/padlock-aes.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/padlock-aes.c

Purpose: registers VIA PadLock ACE AES cipher and ECB/CBC skcipher implementations using x86 `rep xcrypt*` instructions with CPU-feature gating and erratum workarounds.

Important APIs and functions: `aes_set_key()` validates key size, prepares PadLock control words, stores encryption/decryption expanded keys, and invalidates per-CPU cached control words. `padlock_aes_encrypt()`/`padlock_aes_decrypt()` implement single-block cipher API. `ecb_aes_encrypt()`/`ecb_aes_decrypt()` and `cbc_aes_encrypt()`/`cbc_aes_decrypt()` walk skcipher virtual mappings and issue PadLock instructions. `padlock_reset_key()` forces hardware key reload when the per-CPU control word changes.

Control flow: module init checks `X86_FEATURE_XCRYPT` and `XCRYPT_EN`, registers the base AES cipher plus ECB/CBC skcipher algorithms, and enables larger prefetch-copy workarounds for VIA Nano family/model/stepping 6/15/2. Encryption chunks use direct instruction calls unless the PadLock prefetch window would cross a page boundary, in which case stack-aligned copy buffers are used.

State and persistence: transform context stores aligned encryption and decryption key schedules, control words, and pointer to decryption key data. Per-CPU `paes_last_cword` caches the last control word used by hardware.

Dependencies and integration: x86 CPU feature matching, PadLock alignment constants, AES software key expansion fallback for key schedules, skcipher walk API, and raw inline assembly opcodes.

Risks and test signals: PadLock prefetch can read beyond the requested block; page-boundary copy guards are critical. The decrypt single-block path resets/stores the encrypt control word around decrypt state, so control-word cache tests matter. Test AES known vectors for 128/192/256-bit keys, ECB/CBC multi-page buffers, page-end inputs, VIA Nano stepping 2 workaround, CPU hotplug/per-CPU cache invalidation after setkey, and module load on unsupported CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/padlock-aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/padlock-sha.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/padlock-sha.c

Purpose: provides VIA PadLock SHA1/SHA256 shash acceleration, including older one-shot/fallback-assisted flow and Nano multi-part hardware update variants.

Important APIs and functions: `padlock_sha1_init()` and `padlock_sha256_init()` seed aligned state. `padlock_sha_update()` processes full blocks through an ahash fallback using imported/exported core state and returns remaining bytes to the shash core. `padlock_sha1_finup()` and `padlock_sha256_finup()` issue `rep xsha1`/`rep xsha256` and byte-swap the digest output; they fall back when the total byte count exceeds the instruction argument range. Nano-specific update functions issue hardware block updates directly. Import/export copy aligned core state and sanitize count alignment.

Control flow: init checks `X86_FEATURE_PHE` and `PHE_EN`, skips Zhaoxin/newer family `>= 0x07` because self-tests fail, selects Nano algorithms for model `>= 0x0f`, and registers SHA1 and SHA256. Non-Nano variants allocate fallback ahash transforms in `init_tfm`; Nano variants avoid fallback for updates.

State and persistence: per-transform context stores fallback ahash for non-Nano algorithms. Per-request state is an aligned shash descriptor buffer large enough for PadLock microcode. No device-global mutable state beyond registered algorithms.

Dependencies and integration: x86 CPU feature matching, PadLock alignment, SHA core state layouts, crypto shash/ahash import/export core helpers, and inline instruction opcodes.

Risks and test signals: hardware requires 128-byte, 16-byte-aligned state; descriptor size and import sanitization prevent faults. Direct digest writes are avoided because output may be unaligned. Test SHA1/SHA256 vectors, multi-update streaming, import/export, unaligned result buffers, large message fallback, Nano and non-Nano paths, and disabled/skipped CPU-family behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/padlock-sha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/Makefile

Purpose: defines the Qualcomm Crypto Engine module composition for the kernel build.

Important build contract: `CONFIG_CRYPTO_DEV_QCE` builds `qcrypto.o` from `core.o`, `common.o`, and `dma.o`. Feature Kconfig options add `sha.o`, `skcipher.o`, and `aead.o` through conditional `qcrypto-*` object lists.

Control flow and integration: the Makefile keeps the platform driver, shared register setup, and DMA helper always present for QCE, while allowing hash, skcipher, and AEAD algorithm families to be compiled independently.

State and persistence: no runtime state. Build state determines which `qce_algo_ops` are present in `core.c`.

Dependencies: Kbuild object aggregation and `CONFIG_CRYPTO_DEV_QCE_{SHA,SKCIPHER,AEAD}`.

Risks and test signals: mismatched Kconfig options can expose references only when a feature object is included. Build-test all feature combinations: core only, each single algorithm family, and all enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.c

Purpose: implements QCE AEAD algorithms for authenc HMAC+CBC DES/3DES/AES and AES-CCM/RFC4309 CCM using DMA scatterlist staging plus shared QCE register programming.

Important APIs and functions: `qce_aead_crypt()` sets encrypt/decrypt flags, computes payload length, handles zero-length and fallback cases, validates CBC and RFC4309 constraints, and enqueues. `qce_aead_async_req_handle()` prepares IV/nonce/AAD, builds source and destination SG tables, maps DMA, submits BAM transfers, and calls `qce_start()`. `qce_aead_done()` terminates DMA, unmaps/free SG tables, checks status, copies/generated tags on encrypt, and verifies non-CCM tags on decrypt. Setkey paths parse authenc keys or CCM salt and mark AES-192/weak 3DES fallback.

Control flow: CCM with AAD creates a formatted padded AAD buffer and may replace source/destination SGs. Non-CCM appends the shared result buffer to destination for result dump. Completion copies the tag from either QCE result dump or the CCM side buffer. Registration builds `qce_alg_template` instances from `aead_def[]` and links them in `aead_algs`.

State and persistence: transform context stores encryption/auth keys, RFC4309 salt, authsize, fallback AEAD, and `need_fallback`. Request context owns dynamic AAD allocation, SG tables, result SG, nonce buffers, lengths, flags, and fallback request.

Dependencies and integration: QCE core queue, `qce_dma_prep_sgs()`, `qce_start()` AEAD register setup, crypto authenc/CCM helpers, DMA mapping, scatterwalk, and fallback AEAD algorithms.

Risks and test signals: `rctx->adata` is allocated for CCM AAD but not visibly freed in completion/error paths, a leak risk. Error cleanup differs by CCM/non-CCM and diff-dst/in-place. Decrypt length subtracts authsize and can underflow if caller validation is insufficient. Test authenc and CCM vectors, RFC4309 assoclen 16/20 checks, zero-length fallback, AES-192 fallback, weak 3DES fallback, in-place/diff-dst, AAD/non-AAD CCM, decrypt tag failure `-EBADMSG`, and DMA-map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.h

Purpose: declares QCE AEAD context structures and the algorithm operations handle used by the QCE core.

Important types: `struct qce_aead_ctx` stores encryption key, authentication key, RFC4309 CCM salt, key lengths, authsize, fallback-needed flag, and fallback AEAD transform. `struct qce_aead_reqctx` stores operation flags, IV pointer/size, source and destination SG state, result and AAD SG entries, allocated SG tables, crypt/assoc lengths, allocated formatted AAD, CCM nonce/result buffers, RFC4309 IV, and trailing fallback request.

Control flow and integration: `to_aead_tmpl()` recovers the enclosing `qce_alg_template` from a registered AEAD transform. `aead_ops` is exported to `core.c` so QCE can register/unregister AEAD algorithms and dispatch queued requests by type.

State and persistence: context fields persist across transform lifetime, especially fallback and key material. Request context fields are per-request and include resources that completion/error paths must free.

Dependencies: shared QCE `common.h`/`core.h`, crypto AEAD APIs, scatterlists, and QCE nonce/key constants.

Risks and test signals: the trailing fallback request requirement affects request-size calculation. Dynamic `adata` and SG tables must be consistently initialized and released. Test fallback request sizing, CCM/RFC4309 IV construction, and all diff-dst/in-place SG table branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/aead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/cipher.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/cipher.h

Purpose: declares QCE skcipher transform/request context structures and the skcipher algorithm-ops export.

Important types: `struct qce_cipher_ctx` holds the raw encryption key, key length, and optional fallback skcipher for AES modes. `struct qce_cipher_reqctx` holds operation flags, IV pointer/size, SG counts, result SG, destination SG table, source/destination SG pointers, crypt length, and trailing fallback request.

Control flow and integration: skcipher code fills request context before queueing; shared register setup in `common.c` reads flags, key, IV, and crypt length. `to_cipher_tmpl()` maps a crypto skcipher transform back to its `qce_alg_template`. `skcipher_ops` is consumed by QCE core registration and dispatch.

State and persistence: transform context persists keys and fallback; request context is transient but its result SG and destination table remain live until DMA completion.

Dependencies: QCE common/core headers, Linux crypto skcipher APIs, scatterlists, and AES/DES key size constraints.

Risks and test signals: fallback request is deliberately last and request-size code depends on that layout. Test AES fallback paths, DES/3DES no-fallback paths, IV update after completion, and DMA cleanup for both in-place and split source/destination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/common.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/common.c

Purpose: contains shared QCE register access and setup for ahash, skcipher, and AEAD requests, plus status/version helpers.

Important APIs and functions: `qce_start()` dispatches by crypto algorithm type. `qce_setup_config()` resets status and writes CE config for pipe pair, burst size, interrupt masks, and endian mode. `qce_auth_cfg()` and `qce_encr_cfg()` translate abstract QCE flags into authentication/encryption segment config bits. `qce_setup_regs_ahash()`, `qce_setup_regs_skcipher()`, and `qce_setup_regs_aead()` program keys, IVs, byte counts, sizes, starts, segment configs, and GO. `qce_check_status()` returns `-ENXIO` on hardware/error/incomplete and `-EBADMSG` on MAC failure. `qce_get_version()` decodes the hardware revision.

Control flow: each setup path first writes base config/status, writes algorithm-specific key/IV/auth state, sets segment sizes and starts, switches to little-endian BAM/result mode, and triggers GO with optional result dump. SHA preserves first/last block state and byte counts; skcipher handles XTS IV/key special layout; AEAD handles HMAC defaults, CCM nonce, tag position, and CCM counter setup.

State and persistence: no private module state; it mutates hardware registers. Request and transform context objects supply the durable software state.

Dependencies and integration: `regs-v5.h` bit definitions, QCE DMA result buffer format, SHA/skcipher/AEAD context headers, Linux crypto constants, and QCE core version/pipe selection.

Risks and test signals: endian conversions differ between SHA/skcipher and AEAD helper paths. AES-192 is accepted by some setkey code but not encoded as a hardware key size, so fallback decisions must be correct. Test register setup indirectly with vectors for every mode, XTS sector and IV behavior, SHA update/final block boundaries, AEAD tag verification, and unsupported v5.0 rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/common.h

Purpose: centralizes QCE algorithm flags, size constants, template structure, and shared helper prototypes.

Important definitions: constants cover sector size, HMAC/cipher key sizes, IV/nonce sizes, burst alignment, algorithm bits for DES/3DES/AES/SHA/HMAC/CMAC, mode bits for CBC/ECB/CTR/XTS/CCM/RFC4309, and direction bits. Predicate macros such as `IS_AES()`, `IS_SHA_HMAC()`, `IS_CCM()`, and `IS_ENCRYPT()` are used throughout setup and algorithm files. `struct qce_alg_template` wraps one registered crypto algorithm with flags, device pointer, optional standard IV, zero-hash pointer, and list entry.

Control flow and integration: algorithm files allocate templates, set flags, and register the union member matching their crypto type. Core dispatch and common register setup use the template to find the QCE device and mode flags.

State and persistence: templates persist for registered algorithm lifetimes and are linked in per-family lists. The header itself has no runtime state.

Dependencies: Linux crypto API headers, AES/hash/skcipher/AEAD internals, and QCE core declarations.

Risks and test signals: flag bit overlap would misprogram hardware, so all feature combinations should be build- and runtime-tested. Template union use requires callers to recover the correct container for each crypto type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/core.c

Purpose: implements the Qualcomm Crypto Engine platform driver, one-slot async request queue, hardware resource acquisition, version validation, and algorithm-family registration.

Important APIs and functions: `qce_handle_queue()` enqueues requests, handles backlog notification, serializes one active request in `qce->req`, and dispatches by crypto type through `qce_handle_request()`. `qce_req_done_work()` completes the active request and starts the next. `qce_async_request_enqueue()` and `qce_async_request_done()` are installed in `struct qce_device` for algorithm files. `qce_check_version()` rejects unsupported v5.0, sets BAM burst size, and derives pipe-pair ID from the RX DMA channel.

Control flow: probe maps MMIO, configures a 32-bit DMA mask, enables optional clocks, votes memory interconnect bandwidth, requests DMA channels and shared buffers, validates version, initializes mutex/work/queue, installs async callbacks, and registers all compiled algorithm families with devm cleanup.

State and persistence: `struct qce_device` stores queue, active request, result, MMIO base, clocks, interconnect path, DMA resources, burst size, pipe pair, and callbacks. Requests persist in `crypto_queue` until dispatched/completed.

Dependencies and integration: platform/OF matches `qcom,crypto-v5.1`, `qcom,crypto-v5.4`, and `qcom,qce`; optional clocks `core`, `iface`, `bus`; interconnect path `memory`; DMA helper; algorithm ops arrays gated by Kconfig.

Risks and test signals: queue depth is one, so backlog behavior and completion work ordering are important. Algorithm registration unwind in `devm_qce_register_algs()` uses the current `ops` variable when unregistering prior families, which is suspicious and should be reviewed. Test probe deferral, absent optional clocks, interconnect errors, unsupported v5.0, request backlog, each Kconfig algorithm combination, and remove/devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/core.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/core.h

Purpose: declares QCE core device state and the algorithm-family callback interface.

Important types: `struct qce_device` owns the crypto queue, mutex, completion work, active request/result, MMIO base, device pointer, clocks, interconnect path, DMA data, burst size, pipe-pair ID, and callbacks used by algorithms to enqueue and finish requests. `struct qce_algo_ops` defines a crypto type plus register/unregister and async request handler callbacks for skcipher, ahash, and AEAD families.

Control flow and integration: core builds a static array of `qce_algo_ops` from enabled Kconfig families, registers them at probe, and uses `async_req_handle` to process dequeued crypto requests. Algorithm files use the callbacks in `qce_device` to share queue and completion handling.

State and persistence: a `qce_device` instance persists for the platform device lifetime and serializes all algorithm requests through one active request pointer.

Dependencies: mutex/workqueue primitives, QCE DMA data, Linux crypto async request types via included files.

Risks and test signals: all algorithms share one hardware queue, so active request ownership must remain consistent after setup errors and DMA callbacks. Test mixed concurrent SHA/skcipher/AEAD submissions and errors before `async_req_done()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.c

Purpose: manages QCE DMA channel acquisition, shared result/ignore buffers, SG-table assembly, DMA descriptor preparation, issue, and termination.

Important APIs and functions: `devm_qce_dma_request()` requests `tx` and `rx` DMA channels, allocates a combined result/ignore buffer, sets `ignore_buf`, and registers devm cleanup. `qce_sgtable_add()` appends up to `max_len` bytes from an existing SG list into a preallocated SG table. `qce_dma_prep_sgs()` prepares RX-channel MEM_TO_DEV and TX-channel DEV_TO_MEM slave SG descriptors, installing the completion callback on the TX descriptor. `qce_dma_issue_pending()` starts both channels; `qce_dma_terminate_all()` terminates both.

Control flow: algorithm files build/mapping SGs, call `qce_dma_prep_sgs()`, issue pending DMA, then program hardware. Completion terminates both channels before unmapping and reading result buffers.

State and persistence: `struct qce_dma_data` holds channel pointers and persistent shared buffers for the device lifetime. SG tables are caller-owned per request.

Dependencies and integration: DMAengine slave SG API, QCE result dump layout, devm cleanup, and algorithm-specific SG construction.

Risks and test signals: channel naming can be confusing because helper parameters use RX/TX from CE perspective while directions are MEM_TO_DEV/DEV_TO_MEM. `qce_sgtable_add()` requires a table with unused entries and valid pages. Test DMA request probe deferral, descriptor prep failures, SG lists longer than max length, in-place versus diff-dst, and termination errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.h

Purpose: defines QCE DMA buffer sizes, result-dump layout, DMA state, and helper prototypes.

Important types and constants: `QCE_BAM_BURST_SIZE` is 64 bytes. Result dumps include authentication IV, authentication byte counts, encryption counter IV, and status words. `QCE_RESULT_BUF_SZ` aligns the result dump to a BAM burst; `QCE_IGNORE_BUF_SZ` reserves two burst sizes. `struct qce_dma_data` stores TX/RX DMA channels, shared result buffer, and ignore buffer.

Control flow and integration: algorithm code appends `result_buf` as a destination SG to capture hardware result dumps; common status/IV code reads from `struct qce_result_dump` after DMA completion. DMA helpers declared here are implemented in `dma.c` and used by SHA, skcipher, and AEAD files.

State and persistence: result and ignore buffers persist for the platform-device lifetime and are reused across serialized requests.

Dependencies: DMAengine and QCE core/algorithm files.

Risks and test signals: buffer sizing must match hardware result dump and BAM burst alignment. Test cache coherency and DMA mapping of the result buffer across all algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/regs-v5.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/regs-v5.h

Purpose: provides the QCE v5 register offsets, bit shifts, masks, and enum values consumed by shared register setup.

Important definitions: offsets cover version/status, segment sizes, GO, encryption segment config, counters/IVs, XTS, authentication segment config, auth IV/nonce/bytecount/expected MAC, global config, encryption keys, XTS keys, and authentication keys. Bit definitions describe version fields, status errors/MAC failure/operation done, config burst/pipe/endian/interrupt masks, auth modes/sizes/key sizes/positions/nonce words, encryption algorithms/modes/key sizes/encode, GO/result dump, and engine availability.

Control flow and integration: `common.c` uses these constants to compose `REG_CONFIG`, `REG_AUTH_SEG_CFG`, `REG_ENCR_SEG_CFG`, and `REG_GOPROC` writes for SHA, skcipher, and AEAD flows.

State and persistence: no runtime state; this is a hardware ABI map. Wrong values persist only as bad MMIO programming during requests.

Dependencies: Linux bitops and QCE v5-compatible hardware.

Risks and test signals: these values are the root of register programming correctness. Test across `qcom,crypto-v5.1` and `v5.4`, especially CCM, XTS, status error decoding, MAC failure, burst/pipe selection, and little-endian result-dump mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/regs-v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.c

Purpose: implements QCE SHA1/SHA256 and HMAC-SHA1/HMAC-SHA256 ahash algorithms with streaming state, DMA result dumps, export/import, and HMAC key preprocessing.

Important APIs and functions: `qce_ahash_init()` seeds standard digest IV and flags. `qce_ahash_update()` buffers incomplete blocks, chains prior buffered bytes with current SG data, holds back one final block, and enqueues hardware work for block-aligned chunks. `qce_ahash_final()` sends the held buffer as the last block or returns zero-message hashes. `qce_ahash_digest()` handles one-shot requests. `qce_ahash_done()` reads result digest and byte count, restores request fields, and completes. `qce_ahash_hmac_setkey()` hashes long HMAC keys using QCE itself.

Control flow: hardware submissions map source SGs plus a result buffer SG, prepare DMA, issue pending, and program registers through `qce_start()`. Register setup in `common.c` uses first/last flags, digest, byte counts, and auth key fields. Registration creates templates from `ahash_def[]`.

State and persistence: request context persists buffer, temporary SG chain, digest, byte counts, total count, first/last flags, original request fields, auth key pointer, and result SG. Transform context stores padded HMAC key. Export/import serializes enough request state for pause/resume.

Dependencies and integration: QCE core queue, DMA helpers, common register setup, SHA constants, crypto wait helpers for long HMAC key hashing, and zero-message hash constants.

Risks and test signals: update logic intentionally holds back a block on exact multiples to let final set last-block state. Using `sg_dma_len()` before DMA mapping in length traversal is suspicious because update has not mapped yet. Test streaming chunk boundaries, exact block multiples, zero-length final/digest, import/export, HMAC long keys, DMA-map errors, and concurrent queued requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.h

Purpose: declares QCE hash context structures, bounds, template conversion helper, and ops export.

Important types: `struct qce_sha_ctx` stores the padded HMAC key. `struct qce_sha_reqctx` holds pending buffer, temporary buffer, digest, buflen, flags, original source/nbytes, SG count, byte count, total count, first/last block booleans, temporary chained SG entries, auth key pointer/length, and result SG.

Control flow and integration: SHA algorithm code stores all streaming state in `qce_sha_reqctx`; common register setup reads the same fields when programming SHA/HMAC/CMAC auth segments. `to_ahash_tmpl()` recovers the QCE template from a crypto transform, and `ahash_ops` is exported to core registration.

State and persistence: request context is export/import capable and persists across update/final calls. Transform context persists HMAC key material.

Dependencies: scatterwalk, SHA1/SHA2 constants, QCE common/core headers, and crypto ahash internals.

Risks and test signals: max block/digest sizes are SHA256-bound, so adding SHA512 would require structural changes. Test request-size DMA alignment, export/import state size, HMAC setup, and all update/final paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/sha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/skcipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qce/skcipher.c

Purpose: implements QCE skcipher algorithms for AES ECB/CBC/CTR/XTS and DES/3DES ECB/CBC with DMA staging and AES software fallbacks.

Important APIs and functions: `qce_skcipher_setkey()` stores AES keys, rejects XTS identical halves, and configures fallback; DES/3DES setkey functions verify keys and reject 3DES duplicate key components. `qce_skcipher_crypt()` validates lengths, handles zero-length no-op, selects fallback for AES-192 and unsuitable XTS lengths, then enqueues. `qce_skcipher_async_req_handle()` builds a destination SG table with an appended result dump, maps source/destination, submits DMA, and calls `qce_start()`. `qce_skcipher_done()` terminates DMA, unmaps/frees, checks status, and copies the returned counter IV to the request IV.

Control flow: registration builds one template per entry in `skcipher_def[]`; AES algorithms get fallback transforms and larger request contexts, while DES/3DES do not. Hardware register setup in `common.c` uses flags and transform key material.

State and persistence: transform context stores key bytes, key length, and fallback skcipher. Request context stores IV pointer, SG state, result SG/table, crypt length, flags, and fallback request. Module parameter `aes_sw_max_len` controls XTS fallback threshold.

Dependencies and integration: QCE core queue, DMA helpers, common register setup, crypto skcipher fallback API, DES/AES key validation, and module parameter configuration.

Risks and test signals: error path returns `-rctx->dst_nents` for invalid dst count, which turns a negative error into a positive value. AES-192 setkey stores fallback key but leaves hardware key copy empty by design because requests must fallback. Test AES/DES/3DES vectors, CTR IV update, XTS sector-size constraints and module parameter, AES-192 fallback, invalid key rejection, in-place/diff-dst SGs, DMA-map failures, and status error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qce/skcipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qcom-rng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/qcom-rng.c

Purpose: provides Qualcomm PRNG/TRNG support as a crypto RNG named `stdrng`/driver `qcom-rng`, with optional hwrng registration for true RNG-compatible devices.

Important APIs and functions: `qcom_rng_read()` polls `PRNG_STATUS` for data availability, reads 32-bit words from `PRNG_DATA_OUT`, rejects zero words, and copies full or partial words to the caller. `qcom_rng_generate()` enables the optional core clock, serializes reads under a mutex, disables the clock, and returns crypto RNG status. `qcom_rng_enable()` initializes LFSR clocks and enables legacy PRNG hardware unless already enabled. `qcom_rng_init()` binds transforms to the singleton probed device and runs enable unless match data says to skip. `qcom_hwrng_read()` exposes the same read path to hwrng.

Control flow: probe allocates device state, maps registers, gets optional clock, stores match data, sets global `qcom_rng_dev`, registers the crypto RNG, and optionally registers hwrng with quality 1024. Remove unregisters crypto RNG and clears the singleton.

State and persistence: `struct qcom_rng` stores mutex, MMIO base, clock, hwrng object, and match data. Global `qcom_rng_dev` is a singleton consumed by all crypto transforms.

Dependencies and integration: platform OF compatibles `qcom,prng`, `qcom,prng-ee`, `qcom,trng`, ACPI `QCOM8160`, optional core clock, crypto RNG API, hwrng API, and iopoll.

Risks and test signals: singleton design assumes one device. hwrng read path does not enable/disable the clock, relying on skip-init/TRNG hardware state or external clocking. Rejecting zero output may treat valid random words as hardware failure if zero is possible. Test crypto_rng generate sizes not divisible by four, timeout handling, PRNG enable path, PRNG-EE skip-init, TRNG hwrng registration, clock-gated reads, and remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/qcom-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/Makefile

Purpose: defines the Rockchip crypto accelerator module build.

Important build contract: `CONFIG_CRYPTO_DEV_ROCKCHIP` builds `rk_crypto.o` from `rk3288_crypto.o`, `rk3288_crypto_skcipher.o`, and `rk3288_crypto_ahash.o`.

Control flow and integration: the core platform driver, skcipher algorithms, and ahash algorithms are always linked together when the Rockchip crypto driver is enabled, matching the shared registration table in `rk3288_crypto.c`.

State and persistence: no runtime state; object composition controls which external algorithm symbols declared in `rk3288_crypto.h` must be provided.

Dependencies: Kbuild and the Rockchip crypto Kconfig symbol.

Risks and test signals: missing either algorithm object breaks the core registration externs. Build-test the driver as built-in and module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.c

Purpose: implements the Rockchip RK3288/RK3328/RK3399 crypto accelerator platform driver, device list, runtime PM, IRQ completion, debugfs stats, and algorithm registration.

Important APIs and functions: `get_rk_crypto()` rotates the global device list and returns a device for algorithm requests. `rk_crypto_get_clks()` bulk-gets clocks and downclocks named variant clocks above allowed maximums. Runtime PM suspend disables clocks and asserts reset; resume enables clocks and deasserts reset. `rk_crypto_irq_handle()` acknowledges interrupts, records DMA error status, and completes the active request. `rk_crypto_register()` registers all skcipher and ahash engine algorithms; `rk_crypto_unregister()` reverses this.

Control flow: probe allocates device state, fetches variant data, resets hardware, maps MMIO, gets clocks/IRQ, allocates and starts a crypto engine, initializes runtime PM, adds the device to a global list, and registers algorithms/debugfs only for the first device. Remove deletes the device and unregisters algorithms/debugfs when the last device is gone.

State and persistence: global `rocklist` stores devices and optional debugfs dentries. Each `rk_crypto_info` stores clocks, reset, MMIO, IRQ, engine, completion, status, and request count. Algorithm templates store per-algorithm stats and a pointer to the first registered device.

Dependencies and integration: OF compatibles, reset controls, clocks, runtime PM, IRQs, crypto engine, debugfs, and extern algorithm templates from skcipher/ahash files.

Risks and test signals: unregister unwind has index mistakes (`rk_cipher_algs[i]` used inside a loop over `k`) and may unregister wrong entries after partial failure. Algorithm templates keep one `dev` pointer even when requests rotate across devices. Test multi-device probe/remove, runtime PM autosuspend, IRQ timeout/error, debugfs output, partial registration failure, and all registered algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.h

Purpose: defines Rockchip crypto register offsets/bits, shared device/variant/context structures, algorithm template declarations, and MMIO access macros.

Important APIs and types: register definitions cover interrupt status/enable, control, configuration, DMA source/length registers, AES, TDES, and hash engines. `struct rockchip_ip` owns the global device list and debugfs state. `struct rk_variant` describes required clocks and maximum rates. `struct rk_crypto_info` stores one hardware instance, runtime resources, crypto engine, completion, and status. Hash and cipher transform/request contexts hold fallback transforms, keys, IV backup, mode, and request state. `struct rk_crypto_tmp` wraps skcipher or ahash engine algorithms with statistics.

Control flow and integration: core driver registers extern `rk_crypto_tmp` templates declared here. Algorithm files use register constants and `CRYPTO_READ`/`CRYPTO_WRITE` to program hardware. `get_rk_crypto()` is the common device selector for algorithm code.

State and persistence: transform contexts persist fallback objects and key material; request contexts persist selected device/mode and fallback requests. Device and global list state persist across requests and probes.

Dependencies: crypto engine, AES/DES/hash APIs, DMA mapping, interrupts, runtime PM, scatterlists, and Rockchip hardware register ABI.

Risks and test signals: register constants include a misspelled `RK_CYYPTO_*` name but values are used as constants. Key/IV sizes and register byte-swap flags are central to correctness. Test compile coverage for all extern templates, runtime PM request paths, and register programming for AES/DES/hash modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_ahash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_ahash.c

Purpose: implements Rockchip SHA1, SHA256, and MD5 ahash algorithms, using hardware only for aligned one-shot digest requests and falling back for streaming or unsupported SG layout.

Important APIs and functions: `rk_ahash_need_fallback()` rejects SGs whose offsets or lengths are not 32-bit aligned. `rk_ahash_digest()` chooses fallback for bad alignment, returns fixed zero-message digests for empty input, selects a device, and queues hardware work. `rk_ahash_reg_init()` flushes hash state, clears digest registers, enables DMA interrupts, writes mode/byteswap config, and programs message length. `rk_hash_run()` resumes runtime PM, maps source SGs, selects hash mode by digest size, starts DMA for each SG, waits for completion, polls hash done status, reads digest registers little-endian, finalizes the crypto-engine request, and autosuspends the device. Init/update/final/finup/import/export methods delegate to fallback transforms.

Control flow: only `digest` takes the hardware path; all streaming methods use software fallback. Hardware processing walks SG entries sequentially, starting HRDMA for each and waiting up to 2 seconds for IRQ completion.

State and persistence: transform context stores fallback ahash. Request context stores selected device, fallback request, mode, and mapped SG count. Algorithm templates hold request/fallback statistics.

Dependencies and integration: Rockchip core device selection, runtime PM, DMA mapping, IRQ completion from `rk3288_crypto.c`, crypto engine ahash API, zero-message hash constants, and fallback ahash algorithms.

Risks and test signals: `rk_hash_unprepare()` unmaps with `sg_nents()` rather than saved mapped count, which can mismatch DMA API expectations. Completion timeout ignores interrupted wait return and relies on status. Poll condition waits for hash status register to become zero. Test SHA1/SHA256/MD5 vectors, zero messages, unaligned SG fallback, multi-SG digest, DMA error interrupt, timeout, runtime PM, and fallback streaming methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_ahash.c -->
