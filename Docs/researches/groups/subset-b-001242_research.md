# subset-b-001242 crypto driver research

This grouped report covers the requested StarFive JH7110 and STM32 crypto source files. Each source section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-hash.c

## Purpose

This file implements the StarFive JH7110 HASH/HMAC acceleration side of the shared `jh7110-cryp` driver. It registers asynchronous ahash engine algorithms for SHA-224, SHA-256, SHA-384, SHA-512, SM3, and their HMAC variants, while using software ahash fallbacks for streaming `init`/`update`/`final`/`export`/`import` operations that the hardware path does not maintain incrementally.

## Important APIs, types, and functions

The code is built around `struct starfive_cryp_ctx`, `struct starfive_cryp_request_ctx`, and the shared device object from `jh7110-cryp.h`. Hardware access is through HASH registers such as `STARFIVE_HASH_SHACSR`, `SHAWDR`, `SHARDR`, `SHAWKR`, and `SHAWKLEN`, plus the shared algorithm FIFO and DMA length registers. `starfive_hash_wait_busy()`, `starfive_hash_wait_hmac_done()`, and `starfive_hash_wait_key_done()` poll hardware status bits. `starfive_hash_hmac_key()` loads the HMAC key into the hardware key FIFO. `starfive_hash_dma_init()` and `starfive_hash_dma_xfer()` configure and run memory-to-device DMA into the accelerator FIFO. `starfive_hash_one_request()` is the crypto-engine request body, and `starfive_hash_digest()` queues one-shot digest work to the engine. `starfive_hash_setkey()` stores short HMAC keys directly and hashes long HMAC keys through `starfive_hash_long_setkey()`.

The algorithm table `algs_sha2_sm3[]` exposes `sha224`, `sha256`, `sha384`, `sha512`, `sm3`, `hmac(sha224)`, `hmac(sha256)`, `hmac(sha384)`, `hmac(sha512)`, and `hmac(sm3)` with priority 200 and fallback-required flags. `starfive_hash_register_algs()` and `starfive_hash_unregister_algs()` are the integration points called by the parent StarFive crypto driver.

## Control flow, state, and persistence

Transform initialization finds a StarFive crypto device, allocates a named lib fallback (`sha256-lib`, `hmac-sha256-lib`, `sm3-lib`, and similar), sets ahash statesize from that fallback, and records whether the transform is HMAC plus the hardware hash mode. Streaming operations simply re-target a fallback request and delegate to the fallback implementation. One-shot `digest` clears the request context, records the source sg list, total length, block size, digest size, and request pointer in `cryp->req.hreq`, then transfers the request to the crypto engine.

For each hardware request, `starfive_hash_one_request()` resets the HASH unit, initializes `rctx->csr.hash.mode`, either loads the HMAC key or starts a normal hash, DMA-transfers each sg entry into the shared FIFO, sets the final bit, waits for completion, optionally waits for HMAC completion, reads digest words from `SHARDR`, and finalizes the ahash request. Runtime state is transient: per-transform key material and mode live in `struct starfive_cryp_ctx`, per-request scatterlist and size fields live in `struct starfive_cryp_request_ctx`, and the hardware register state is reset before each engine request. No file-backed or cross-boot state is persisted.

## Dependencies and integration points

The driver depends on the Linux crypto engine and ahash APIs, `crypto/internal/hash.h`, scatterwalk helpers, DMAengine slave transfers, completions, I/O polling, the shared StarFive crypto device and CSR bit definitions in `jh7110-cryp.h`, and parent driver resource setup for MMIO, physical FIFO address, DMA channel `tx`, and `dma_maxburst`. It integrates with the crypto API as async ahash algorithms and with the parent JH7110 crypto module through the exported register/unregister functions.

## Risks and test signals

The main risks are DMA mapping and alignment behavior, the direct assignment to `sg_dma_len(sg)` after programming the real hardware byte count, timeout paths that return before all engine-side state is naturally finalized, and long HMAC key handling that hashes via the driver's own registered algorithm names. The streaming API is intentionally fallback-backed, so test coverage must distinguish one-shot hardware digest from fallback streaming behavior. Useful signals are crypto selftests for every SHA2/SM3 and HMAC variant, comparison against software fallbacks for zero-length and multi-sg messages, HMAC keys shorter and longer than the block size, DMA timeout/error injection where possible, and module load/unload verifying algorithm registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-rsa.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-rsa.c

## Purpose

This file implements RSA public-key acceleration for the StarFive JH7110 crypto block. It exposes the kernel `akcipher` algorithm name `rsa` with driver name `starfive-rsa`, parses public and private RSA keys, uses the hardware PKA registers for modular exponentiation in Montgomery form, and falls back to `rsa-generic` when no suitable hardware key is installed.

## Important APIs, types, and functions

The PKA register interface uses offsets under `STARFIVE_PKA_REGS_OFFSET`: control/status (`CACR`, `CASR`), operand/result (`CAAR`), exponent (`CAER`), and modulus (`CANR`). The command constants describe Montgomery preprocessing and multiply/exponent operations: `CRYPTO_CMD_PRE`, `CRYPTO_CMD_ARN`, `CRYPTO_CMD_AERN`, and `CRYPTO_CMD_AARN`. `starfive_pka_wait_done()` polls `STARFIVE_PKA_DONE`. Key lifetime is managed by `starfive_rsa_free_key()`, `starfive_rsa_set_n()`, `starfive_rsa_set_e()`, `starfive_rsa_set_d()`, and `starfive_rsa_setkey()`.

The core math path is `starfive_rsa_montgomery_form()` and `starfive_rsa_cpu_start()`. The latter converts the message into Montgomery form, writes it as the active operand, performs square-and-multiply over exponent bits from `starfive_rsa_get_nbit()`, reads the result, and converts out of Montgomery form. `starfive_rsa_enc_core()` copies request data from sg into an aligned buffer, selects public exponent or private exponent, invokes the PKA path, copies the result to the destination sg, and resets the PKA block. `starfive_rsa_enc()` and `starfive_rsa_dec()` implement akcipher encrypt/decrypt entry points.

## Control flow, state, and persistence

Transform initialization finds the shared StarFive crypto device, allocates a `rsa-generic` fallback, and sets an akcipher request size. `set_pub_key` and `set_priv_key` first configure the fallback, then parse DER-encoded RSA keys through `rsa_parse_pub_key()` or `rsa_parse_priv_key()`. If the modulus is larger than the hardware maximum plus one possible leading-zero byte, the StarFive key is left empty so subsequent operations use the fallback. Otherwise, modulus, exponent, and optional private exponent are stored right-aligned in `struct starfive_rsa_key` with bit lengths derived from the first nonzero byte.

Encrypt/decrypt requests validate that the required key components are present and that `dst_len` can hold the modulus-sized result. The hardware path is synchronous: it resets PKA, pads unaligned input at the front of `rctx->rsa_data`, copies from source sg, executes modular exponentiation, copies exactly `key_sz` bytes to destination sg, then resets PKA again. Persistent state is limited to per-transform key buffers and the fallback transform; all request buffers and PKA register contents are transient.

## Dependencies and integration points

The file depends on the kernel akcipher API, RSA key parsers from `crypto/internal/rsa.h`, scatterlist copy helpers, MMIO polling, and shared StarFive crypto structures from `jh7110-cryp.h`. `starfive_rsa_register_algs()` and `starfive_rsa_unregister_algs()` are the parent-driver hooks. The algorithm advertises `CRYPTO_ALG_NEED_FALLBACK` and priority 3000, so it participates in normal crypto API lookup while retaining `rsa-generic` for unsupported key sizes or pre-key operations.

## Risks and test signals

Risks cluster around endian/layout assumptions for operand arrays, leading-zero key normalization, modulus-size limits, front-padding of non-word-aligned input, and the hand-written square-and-multiply loop. The operation is synchronous and polls up to 100 ms per PKA command, so large exponents can create latency under crypto API callers. There is no blinding in this hardware path, which matters for private-key side-channel review. Test signals include RSA selftests for public and private keys at supported sizes, leading-zero modulus encodings, fallback behavior for oversized keys, insufficient `dst_len` returning `-EOVERFLOW`, unaligned source lengths, and repeated encrypt/decrypt cycles verifying that PKA reset leaves later requests independent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-rsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/stm32/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/stm32/Kconfig

## Purpose

This Kconfig file defines the build-time configuration switches for the STM32 crypto accelerator drivers: `CRYPTO_DEV_STM32_HASH` for HASH hardware and `CRYPTO_DEV_STM32_CRYP` for CRYP AES/DES/TDES hardware.

## Important APIs, types, and functions

There are no functions or runtime types. `CRYPTO_DEV_STM32_HASH` is a tristate option named "Support for STM32 hash accelerators"; it depends on `ARCH_STM32 || ARCH_U8500` and `HAS_DMA`, selects the hash algorithms and infrastructure it may register (`CRYPTO_HASH`, `CRYPTO_MD5`, `CRYPTO_SHA1`, `CRYPTO_SHA256`, `CRYPTO_SHA512`, `CRYPTO_SHA3`, and `CRYPTO_ENGINE`). `CRYPTO_DEV_STM32_CRYP` is a tristate option named "Support for STM32 cryp accelerators"; it depends on `ARCH_STM32 || ARCH_U8500` and selects `CRYPTO_HASH`, `CRYPTO_ENGINE`, and `CRYPTO_LIB_DES`.

## Control flow, state, and persistence

Kconfig only controls compilation. When enabled as built-in or module, the corresponding Makefile entries build `stm32-hash.o` and/or `stm32-cryp.o`. There is no runtime state in this file and no persistence beyond the kernel configuration.

## Dependencies and integration points

The dependencies align the drivers with STM32 and Ux500 SoC families. HASH explicitly requires DMA support because the driver contains DMA code paths and registers algorithms that use crypto engine request routing. CRYP selects DES library support because its skcipher registrations validate DES and 3DES keys. Both options integrate with the crypto subsystem through `CRYPTO_ENGINE`.

## Risks and test signals

The main configuration risk is dependency drift: `stm32-hash.c` also supports polling and CPU paths, but the Kconfig still requires `HAS_DMA`; `stm32-cryp.c` can continue without DMA channels at runtime but still depends on platform support and selected libraries. Test signals are successful builds for `m`, `y`, and disabled configurations on STM32/Ux500 defconfigs, correct module objects being emitted, and no unresolved crypto symbols when either option is selected independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/stm32/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/stm32/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/stm32/Makefile

## Purpose

This Makefile connects the STM32 crypto Kconfig symbols to their driver objects.

## Important APIs, types, and functions

There are no C APIs. The file has two object rules: `obj-$(CONFIG_CRYPTO_DEV_STM32_HASH) += stm32-hash.o` and `obj-$(CONFIG_CRYPTO_DEV_STM32_CRYP) += stm32-cryp.o`.

## Control flow, state, and persistence

Build control is entirely declarative. If a symbol is built-in, the object is linked into the kernel image; if it is a module, the corresponding `.ko` is produced; if disabled, the object is omitted. No runtime state or persistence exists here.

## Dependencies and integration points

The Makefile is paired with `drivers/crypto/stm32/Kconfig` and the parent crypto drivers Makefile. Its integration point is kbuild's `obj-*` expansion for `stm32-hash.c` and `stm32-cryp.c`.

## Risks and test signals

Risks are limited to stale object names or mismatched Kconfig symbols. Test by building the two symbols independently as modules and built-ins, confirming `stm32-hash.o` and `stm32-cryp.o` are included only under their configured options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/stm32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/stm32/stm32-cryp.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/stm32/stm32-cryp.c

## Purpose

This platform driver exposes STM32 and Ux500 CRYP hardware through the kernel crypto API. It registers async skcipher algorithms for AES ECB/CBC/CTR, DES ECB/CBC, and 3DES ECB/CBC, plus AES-GCM and AES-CCM AEAD algorithms on hardware variants that support AEAD modes. It handles SoC-specific register layouts, AES key programming quirks, DMA or interrupt-driven data movement, GCM/CCM phase sequencing, runtime power management, and crypto-engine serialization.

## Important APIs, types, and functions

`struct stm32_cryp_caps` describes variant features and register offsets, including AEAD support, Ux500 linear AES keys, key-preparation mode, IV protection, final-size endian swapping, and padding workarounds. `struct stm32_cryp_ctx` stores per-transform key material and key length. `struct stm32_cryp_reqctx` stores the requested algorithm/mode flags. `struct stm32_cryp` is the device state: MMIO, clock, caps, engine, current skcipher or AEAD request, sizes for header/payload/auth data, DMA channels and sg slices, interrupt scatterwalks, and GCM/CTR counters.

Important setup helpers are `stm32_cryp_find_dev()`, `stm32_cryp_hw_write_key()`, `stm32_cryp_hw_write_iv()`, `stm32_cryp_get_hw_mode()`, and `stm32_cryp_hw_init()`. AEAD setup is split through `stm32_cryp_gcm_init()`, `stm32_cryp_ccm_init()`, `stm32_cryp_write_ccm_first_header()`, and `stm32_crypt_gcmccm_end_header()`. Request routing uses `stm32_cryp_crypt()`, `stm32_cryp_aead_crypt()`, `stm32_cryp_cipher_one_req()`, `stm32_cryp_aead_one_req()`, and `stm32_cryp_prepare_req()`. Data movement is selected by `stm32_cryp_dma_check()`, `stm32_cryp_cipher_prepare()`, `stm32_cryp_aead_prepare()`, `stm32_cryp_dma_start()`, `stm32_cryp_header_dma_start()`, and `stm32_cryp_it_start()`. Interrupt processing is handled by `stm32_cryp_irq()` and `stm32_cryp_irq_thread()`, which call block read/write helpers and AEAD padding workarounds.

## Control flow, state, and persistence

Probe maps MMIO, reads match data, requests a threaded IRQ, enables the clock, initializes runtime PM and optional reset, tries to allocate DMA channels, adds the device to a global list, starts a one-deep crypto engine, registers skcipher algorithms, and conditionally registers AEAD algorithms. Transform init only sets request context size; setkey validates and stores AES/DES/3DES keys. Each encrypt/decrypt entry validates block-size and zero-length behavior, stores mode flags in the request context, and queues the request to the engine.

For a queued request, `stm32_cryp_prepare_req()` installs the current transform and mode into the device, derives hardware block size, computes payload/header/auth lengths, starts scatterwalks, chooses DMA or interrupt mode, and initializes hardware. Hardware init programs data type, key size, algorithm mode, decrypt bit, key registers, IV registers, and for AES ECB/CBC decrypt runs a key-preparation phase before normal decrypt. GCM and CCM requests enter hardware init/header/payload/final phases; finalization reads or verifies the authentication tag, updates IV for stateful skcipher modes, drops runtime PM usage, and finalizes the crypto-engine request. Runtime state persists only within the active request and per-transform key. Hardware registers are rewritten per request, while runtime PM preserves only clock state.

## Dependencies and integration points

The driver depends on the crypto engine, skcipher and AEAD internals, AES/DES helper validation, scatterwalk, DMAengine, platform devices, OF match data, clocks, resets, threaded IRQs, and runtime PM. It matches `stericsson,ux500-cryp`, `st,stm32f756-cryp`, and `st,stm32mp1-cryp`. It registers algorithms with `CRYPTO_ALG_ASYNC | CRYPTO_ALG_KERN_DRIVER_ONLY` and priority 300. The parent build integration is the STM32 crypto Kconfig/Makefile pair.

## Risks and test signals

The highest-risk areas are AEAD phase transitions, partial final block padding for GCM encryption and CCM decryption, DMA sg truncation and cleanup, CTR counter carry handling, Ux500 key swizzling, AES decrypt key-preparation ordering, and timeout paths that must complete or abort requests without leaving DMA mappings or runtime PM references behind. The code also depends on global first-device selection for transforms. Test signals include crypto selftests for all registered skcipher and AEAD modes, in-place and out-of-place sg lists, short messages that force interrupt mode, aligned and unaligned sg lists that select DMA truncation, GCM/CCM AAD-only and payload-only cases, tag verification failure returning `-EBADMSG`, CTR counter wrap near `0xffffffff`, suspend/resume with runtime PM, and module remove after active algorithm registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/stm32/stm32-cryp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/stm32/stm32-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/stm32/stm32-hash.c

## Purpose

This platform driver exposes STM32 and Ux500 HASH accelerators through the async hash crypto API. Depending on the matched hardware, it registers MD5, SHA1, SHA224, SHA256, SHA384, SHA512, SHA3-224/256/384/512, and HMAC variants. It supports CPU-fed and DMA-fed hashing, resumable ahash state export/import through hardware context registers, Ux500-specific limitations, optional IRQ or polling completion, runtime PM, and crypto-engine serialization.

## Important APIs, types, and functions

`struct stm32_hash_ctx` stores the selected device, optional Ux500 shash fallback, flags for HMAC/SHA3 modes, and HMAC key material. `struct stm32_hash_state` is the exported/imported request state: flags, buffered byte count, block length, buffered data, and saved hardware context registers. `struct stm32_hash_request_ctx` tracks the active operation, digest buffer, sg state, DMA mapping state, data type, and embedded `stm32_hash_state`. `struct stm32_hash_pdata` describes variant algorithm tables and quirks such as status-register presence, multiple-DMA mode, secured context-save behavior, broken empty-message handling, and Ux500 register format. `struct stm32_hash_dev` stores MMIO, clock/reset, DMA, completion, current request, crypto engine, and runtime flags.

Important helpers include `stm32_hash_write_ctrl()` for CR programming, `stm32_hash_write_key()` for HMAC key injection, `stm32_hash_xmit_cpu()` and `stm32_hash_update_cpu()` for CPU-fed transfers, `stm32_hash_xmit_dma()`, `stm32_hash_dma_send()`, and `stm32_hash_hmac_dma_send()` for DMA-fed transfers, `stm32_hash_prepare_request()` and `stm32_hash_unprepare_request()` for sg alignment and hardware-context save/restore, `stm32_hash_one_request()` as the crypto-engine body, `stm32_hash_finish_req()` for completion, and `stm32_hash_register_algs()` for variant-selected algorithm registration.

## Control flow, state, and persistence

Probe maps registers, obtains variant pdata from OF, requests an optional IRQ or enables polling mode, enables the clock, initializes runtime PM and optional reset, tries to set up an input DMA channel, adds the device to a global list, starts a one-deep crypto engine, reads hardware DMA capability, and registers only the algorithm sets listed by the matched pdata. Transform init sets request size, records HMAC/SHA3 flags, and on Ux500 allocates a software shash fallback for broken empty-message handling.

`stm32_hash_init()` binds the request to a device, selects the hardware algorithm from digest size and SHA3/Ux500 flags, initializes buffer and block accounting, marks CPU mode when DMA or multi-DMA is unavailable, and marks HMAC requests. `update` buffers small data locally until enough data is available; larger updates enqueue to the engine. `final` marks final state and enqueues; `finup` combines update and final. The engine body restores prior hardware context if this is a resumed hash, prepares DMA sg alignment if needed, runs update or final via CPU or DMA, handles polling if no IRQ exists, and saves hardware context during unprepare unless the request has fully finalized. Final requests read digest registers, apply Ux500 empty-message fallback when required, copy the digest to `req->result`, release runtime PM, and finalize the crypto-engine request.

State persistence is per-request and explicit: `export` copies `struct stm32_hash_state`, and `import` initializes a request then copies that state back. Hardware context registers are saved into `state.hw_context` after partial operations and restored before later operations. Per-transform HMAC keys remain in `struct stm32_hash_ctx`; device runtime state and MMIO registers are transient.

## Dependencies and integration points

The driver depends on crypto engine and ahash internals, shash fallback support for Ux500, MD5/SHA1/SHA2/SHA3 definitions, scatterwalk, DMAengine, platform/OF, clocks, resets, optional threaded IRQs, polling helpers, and runtime PM. It matches `stericsson,ux500-hash`, `st,stm32f456-hash`, `st,stm32f756-hash`, and `st,stm32mp13-hash`, each with different algorithm coverage. Algorithms are registered as async kernel-driver-only ahash implementations with priority 200.

## Risks and test signals

Risk areas include context save/restore sizing per algorithm and HMAC mode, DMA alignment and temporary sg allocation/freeing, final-block and `NBLW` accounting, HMAC key handling for long and short keys, Ux500 empty-message fallback, polling-vs-IRQ completion, and runtime PM balance when preparation fails. The code contains an explicit unsupported case when deferred buffered data exceeds one block, so boundary tests matter. Strong test signals are crypto manager tests for every registered hash and HMAC variant on each compatible, update/final/export/import sequences, DMA and CPU paths, zero-length messages on Ux500 and STM32, unaligned sg offsets, long HMAC keys up to `HASH_MAX_KEY_SIZE`, SHA3 mode selection on STM32MP13, operation without IRQ in polling mode, suspend/resume, and clean module removal after algorithm unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/stm32/stm32-hash.c -->
