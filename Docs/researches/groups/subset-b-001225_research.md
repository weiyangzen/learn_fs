# subset-b-001225 research

This grouped report covers Chelsio T6 crypto offload, Exynos PRNG crypto API integration, Gemini SL3516 crypto engine AES/RNG support, and AMD Geode LX AES offload. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_algo.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_algo.c

Purpose: implements the Linux Crypto API algorithms exposed by the Chelsio T6 crypto lookaside engine. It registers skcipher AES CBC/CTR/XTS/RFC3686, SHA and HMAC ahash, GCM/CCM/RFC4106/RFC4309 AEAD, and authenc combinations, translating requests into Chelsio firmware crypto work requests and falling back to software when request shape or hardware limits cannot be satisfied.

Important APIs and control flow: `start_crypto()` and `stop_crypto()` call the local registration/unregistration loop over `driver_algs`. Per-TFM init paths allocate fallback transforms and bind the TFM to a selected `chcr_dev` through `chcr_device_init()`. Cipher requests enter `chcr_aes_encrypt()` or `chcr_aes_decrypt()`, choose CPU-derived TX/RX queues, map DMA, decide immediate versus SGL payload, build a WR in `create_cipher_wr()`, and continue multi-WR requests from `chcr_handle_cipher_resp()`. Hash requests use `chcr_ahash_update()`, `final()`, `finup()`, `digest()`, `chcr_ahash_continue()`, and `create_hash_wr()` to carry partial digest state across hardware fragments. AEAD requests pass through `chcr_aead_encrypt()` or `chcr_aead_decrypt()`, select `create_authenc_wr()`, `create_aead_ccm_wr()`, or `create_gcm_wr()`, and verify tags in hardware or with `chcr_verify_tag()`.

State and persistence behavior: TFM contexts persist keys, reverse-round AES keys, HMAC ipad/opad states, GHASH H, salt/nonce, hardware key context headers, fallback TFMs, and device queue geometry. Per-request contexts persist mapped SG walkers, offsets, IV/tweak state, immediate flags, operation direction, verification mode, and partially processed byte counts. Runtime device state is protected by `chcr_inc_wrcount()` and `chcr_dec_wrcount()` so detach waits for in-flight work before freeing lower-layer resources. Hardware output updates IVs, partial hashes, and completion status; software fallback is used for zero-length, unsupported key/request geometry, CTR overflow boundaries, excessive SGs, or unsupported tag truncation.

Dependencies and integration points: depends on Chelsio `cxgb4` ULD plumbing, `t4fw_api.h`, `t4_msg.h`, `chcr_core.h`, `chcr_algo.h`, and `chcr_crypto.h`, plus Linux Crypto API internals, DMA mapping, scatterlists, AES helpers, HMAC prepare helpers, GF(2^128) tweak math, and firmware work-request/CPL formats. `chcr_handle_resp()` is called by the core RX handler when firmware returns `CPL_FW6_PLD`; `chcr_send_wr()` is supplied by core code.

Risks and test signals: risks include very complex SG length accounting, queue-full paths that must always decrement inflight counts, `BUG()` in unexpected request-type handling, `BUG_ON()`-style assumptions delegated to hardware completion paths, key material lifetime in long-lived contexts, subtle IV/tweak updates for fragmented CBC/CTR/XTS, software tag verification for unusual GCM tag sizes, and many hand-packed big-endian firmware fields. Test signals include `cryptomgr` self-tests for every registered algorithm, fallback counters under misaligned/oversized/zero-length cases, DMA map/unmap balance under error injection, detach waiting for inflight requests, RFC4106/RFC4309 assoclen validation, AEAD bad-tag returning `-EBADMSG`, fragmented requests completing with correct final IV/result, and no crypto registration leaks after partial registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_algo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_algo.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_algo.h

Purpose: defines Chelsio crypto work-request helper macros, key context bit fields, hash constants, request parameter containers, AES key schedule helpers, and scatter/gather sizing utilities used by `chcr_algo.c`.

Important APIs and control flow: the header exposes bitfield macros such as `FILL_SEC_CPL_OP_IVINSR()`, `FILL_SEC_CPL_CIPHERSTOP_HI()`, `FILL_SEC_CPL_AUTHINSERT()`, `FILL_SEC_CPL_SCMD0_SEQNO()`, `FILL_SEC_CPL_IVGEN_HDRLEN()`, `FILL_KEY_CTX_HDR()`, `FILL_WR_OP_CCTX_SIZE`, `FILL_WR_RX_Q_ID()`, and `FILL_ULPTX_CMD_DEST()` that pack firmware and CPL fields in network byte order. `TRANSHDR_SIZE()`, `CIPHER_TRANSHDR_SIZE()`, `HASH_TRANSHDR_SIZE()`, `CIP_SPACE_LEFT()`, and `HASH_SPACE_LEFT()` size WR payloads. `struct algo_param`, `struct hash_wr_param`, and `struct cipher_wr_param` carry computed control values into WR builders. `copy_hash_init_values()` seeds SHA/SHA2 partial-hash buffers, `get_space_for_phys_dsgl()` computes physical DSGL byte consumption, and `aes_ks_subword()` supports software AES reverse key generation.

State and persistence behavior: the header owns only static constants and inline calculations. Its SHA initial vectors, AES S-box, and field encodings become immutable compile-time data inside users. Persistent hardware state is described indirectly through packed control words and key-context headers; request-specific state is stored by structures filled by `chcr_algo.c`.

Dependencies and integration points: depends on Chelsio CPL/ULP/FW bitfield macros from included message headers and on crypto SHA/AES constants. Its definitions are tightly coupled to `struct chcr_wr`, `_key_ctx`, firmware lookaside WR layout, and the Chelsio T6 security PDU field definitions.

Risks and test signals: risks include invalid field shifts silently creating malformed hardware requests, DSGL sizing needing to match descriptor packing exactly, `FILL_KEY_CTX_HDR()` always setting salt-present, endian assumptions in `aes_ks_subword()`, and hash initial state conversion differences between 32-bit and 64-bit digests. Test signals include compile coverage of all WR builders, byte-for-byte validation of generated CPL/FW fields against hardware documentation, successful SHA/HMAC initial digest self-tests, 128/192/256-bit key context sizing, and no SGE overrun for maximum supported SG counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_algo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_core.c

Purpose: provides the Chelsio crypto ULD core that binds the crypto algorithm layer to the `cxgb4` adapter driver. It manages active/inactive crypto devices, handles adapter state changes, receives firmware completions, and starts/stops Crypto API algorithm registration when hardware becomes available.

Important APIs and control flow: module init initializes `drv_data` lists and registers `chcr_uld_info` with `cxgb4_register_uld()`. `chcr_uld_add()` validates `ULP_CRYPTO_LOOKASIDE`, allocates `struct uld_ctx`, copies lower-layer device information, and calls `chcr_dev_init()`. On `CXGB4_STATE_UP`, `chcr_uld_state_change()` moves the device active with `chcr_dev_add()` and calls `start_crypto()`. On detach it calls `chcr_detach_device()`, waits for in-flight operations through delayed work and a completion, moves the device inactive, and calls `stop_crypto()` when no devices remain. `chcr_uld_rx_handler()` dispatches CPL responses to `cpl_fw6_pld_handler()`, which recovers the original `crypto_async_request` cookie, translates firmware MAC/padding errors into `-EBADMSG`, and calls `chcr_handle_resp()`.

State and persistence behavior: global `drv_data` stores active and inactive device lists, a round-robin `last_dev`, device count, and a mutex. Each `chcr_dev` tracks state, in-flight request count, detach retry budget, delayed detach work, and detach completion. `assign_chcr_device()` selects an active device round-robin so a TFM stays bound to one device while new TFMs distribute across adapters.

Dependencies and integration points: depends on `cxgb4_uld` callbacks, adapter stats, CPL_FW6_PLD response format, skb send path `cxgb4_crypto_send()`, and algorithm-layer exports `start_crypto()`, `stop_crypto()`, and `chcr_handle_resp()`. PCI driver data links `chcr_dev` to the Chelsio adapter through `padap()`.

Risks and test signals: risks include list/round-robin edge cases when detaching the current `last_dev`, long waits if inflight requests never complete, freeing ULD contexts only at module exit, response cookies being trusted as kernel pointers, and partial algorithm registration when multiple adapters race state transitions. Test signals include ULD add rejection without lookaside support, state-up registering algorithms once, detach waiting until inflight reaches zero, error stats incrementing on MAC/pad failures, unsupported CPL opcode logging, and module unload clearing stats and freeing all active/inactive contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_core.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_core.h

Purpose: declares the Chelsio crypto core ABI shared by the ULD core and algorithm implementation: module names, detach timing constants, work-request container layout, device lists, device state, ULD context, and core entry points.

Important APIs and control flow: `struct chcr_driver_data` defines the global active/inactive device manager. `enum chcr_state` describes INIT, ATTACH, and DETACH states. `struct chcr_wr` lays out a firmware lookaside WR followed by ULP TX packet metadata, immediate data command, security CPL, and flexible key context. `struct chcr_dev` contains locking, state, inflight count, delayed detach work, and completion state. `struct uld_ctx` embeds `cxgb4_lld_info` plus `chcr_dev`. Helpers include `sgl_len()` for Chelsio ULP SGL flit sizing and `padap()` for recovering the adapter from a crypto device.

State and persistence behavior: the header fixes the in-memory layout used by both core and algorithm files. Runtime persistence is in the global driver lists and per-device in-flight/detach state; WR contents are per-request and sent through skb payloads. Constants such as `WQ_RETRY` and `WQ_DETACH_TM` define how long detach can poll for outstanding completions.

Dependencies and integration points: depends on Chelsio hardware headers (`t4_hw.h`, `cxgb4.h`, `t4_msg.h`, `cxgb4_uld.h`), Linux Crypto API request types, TLS include exposure through Chelsio headers, workqueue/completion infrastructure, and the firmware/CPL structures embedded in `struct chcr_wr`. It exports `assign_chcr_device()`, `chcr_send_wr()`, `start_crypto()`, `stop_crypto()`, `chcr_uld_rx_handler()`, and `chcr_handle_resp()`.

Risks and test signals: risks include `struct chcr_wr` relying on flexible key storage and exact firmware layout, `sgl_len()` underflow if called with zero entries, detach retry constants being too short for long hardware operations, and shared header coupling to many low-level Chelsio definitions. Test signals include compile-time layout compatibility with firmware macros, successful skb WR construction for min/max key contexts, correct adapter recovery through `padap()`, and detach behavior under sustained request load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_crypto.h

Purpose: defines Chelsio crypto algorithm constants, Crypto API context layouts, per-request state structures, SG walker state, algorithm template union, and prototypes shared by `chcr_algo.c`.

Important APIs and control flow: constants encode Chelsio SCMD cipher modes, auth modes, HMAC truncation controls, key context sizes, AEAD subtype bits, priority values, maximum IV/key/scratch/hash sizes, and SG chunk limits. Context helpers `a_ctx()`, `c_ctx()`, and `h_ctx()` recover `struct chcr_context` from AEAD, skcipher, and ahash TFMs. `struct ablk_ctx`, `chcr_aead_ctx`, `chcr_gcm_ctx`, `chcr_authenc_ctx`, and `hmac_ctx` hold per-TFM key and auth material. `struct chcr_aead_reqctx`, `chcr_skcipher_req_ctx`, and `chcr_ahash_req_ctx` hold per-request DMA, SG, IV, completion, and partial-hash state. Prototypes expose DMA map/unmap and SGL population helpers for AEAD, cipher, and hash paths.

State and persistence behavior: per-TFM state persists fallback transforms, hardware key headers, key bytes, salts/nonces, GHASH subkey, HMAC pads, queue geometry, and CBC completion state. Per-request state persists mapped IV/B0 buffers, immediate mode decisions, TX/RX queue indices, SG offsets, partial progress, and fallback subrequests. The flexible `struct chcr_context` ends in a union that is sized by each registered algorithm's `cra_ctxsize`.

Dependencies and integration points: depends on Linux Crypto API types, AES constants, scatterlists, `sk_buff`, `hwrng`-unrelated Chelsio core state, and the firmware field values consumed by `chcr_algo.h`. The subtype constants are embedded in `driver_algs` and drive request dispatch.

Risks and test signals: risks include flexible-array context sizing mistakes, request contexts with fallback request objects that must remain last, stale key material unless TFM exit paths free/clear fallback state, small `MAX_DSGL_ENT` and SG chunk constants controlling fallback boundaries, and debug comments documenting assumptions about hardware AAD/IV dropping. Test signals include correct Crypto API reqsize for every algorithm, KASAN coverage for flexible context users, successful fallback subrequest execution, queue index propagation into WR cookies, and AEAD/cipher/hash DMA helper balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/chelsio/chcr_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/exynos-rng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/exynos-rng.c

Purpose: implements a Crypto API `rng_alg` named `stdrng` backed by the Exynos4 RNG or Exynos5250 PRNG hardware. It maps platform MMIO, controls the `secss` clock, accepts explicit seeds, generates random bytes in 20-byte hardware chunks, periodically reseeds itself from generated output, and preserves seed material across suspend/resume.

Important APIs and control flow: `exynos_rng_probe()` enforces a single global device, allocates `struct exynos_rng_dev`, reads match data for Exynos4 versus Exynos5 behavior, gets the `secss` clock, maps registers, stores the global `exynos_rng_dev`, and registers `exynos_rng_alg`. `exynos_rng_seed()` enables the clock, locks the device, and calls `exynos_rng_set_seed()`, which writes five seed registers in big-endian byte order and checks `EXYNOS_RNG_STATUS_SEED_SETTING_DONE`. `exynos_rng_generate()` enables the clock, loops over `exynos_rng_get_random()`, and calls `exynos_rng_reseed()` after each chunk. Exynos4 starts generation through `EXYNOS_RNG_CONTROL_START`; Exynos5 uses `EXYNOS_RNG_GEN_PRNG`.

State and persistence behavior: global `exynos_rng_dev` means only one hardware RNG instance can register. Per-device state stores MMIO base, clock, mutex, PRNG type, saved resume seed, last seeding jiffies, and byte count since seeding. Reseed occurs after one second or 65536 generated bytes, using freshly generated output as the next seed. Suspend stores one generated seed block if the device was ever seeded; resume reseeds from that saved block.

Dependencies and integration points: depends on platform device/OF matching for `samsung,exynos4-rng` and `samsung,exynos5250-prng`, the `secss` clock, Crypto API internal RNG registration, runtime MMIO access, mutexes, and PM hooks. Consumers interact through the kernel Crypto API `stdrng` interface rather than `hwrng`.

Risks and test signals: risks include fixed global singleton behavior, polling with no sleep and only 100 retries, no entropy quality reporting through hwrng, reseeding from generated output rather than external entropy, seed writes requiring at least exactly five registers, ignored suspend random-generation failure except saved length, and potential overrun assumptions if caller buffers are not word aligned are avoided by `memcpy_fromio()`. Test signals include crypto RNG self-tests, seed rejection below 20 bytes, timeout handling when `RNG_DONE` never sets, Exynos4 and Exynos5 start-register behavior, suspend/resume reseeding after prior seed, and clock enable/disable balance under generate and seed failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/exynos-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/gemini/Makefile

Purpose: declares the object composition for the Gemini/Storlink SL3516 crypto engine driver.

Important APIs and control flow: when `CONFIG_CRYPTO_DEV_SL3516` is enabled, the build creates the `sl3516-ce.o` module or built-in object. The composite object is formed from `sl3516-ce-core.o`, `sl3516-ce-cipher.o`, and `sl3516-ce-rng.o`, which respectively provide platform/device registration, skcipher offload, and hwrng registration.

State and persistence behavior: the Makefile has no runtime state. Its persistent effect is link-time inclusion of all three driver components under one Kconfig symbol, so cipher and RNG support are not independently selectable.

Dependencies and integration points: depends on the parent crypto driver Kconfig selecting `CONFIG_CRYPTO_DEV_SL3516`. The object list assumes all shared declarations live in `sl3516-ce.h` and that core code calls the cipher and RNG helper entry points.

Risks and test signals: risks include unresolved symbols if any component is omitted, inability to build only RNG or only cipher support, and Kconfig dependency mistakes surfacing only at link or modpost time. Test signals are successful `CONFIG_CRYPTO_DEV_SL3516=m` and built-in builds, module containing platform driver plus hwrng and skcipher symbols, and no stale object names after file renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-cipher.c

Purpose: implements AES ECB skcipher offload for the Storlink/Cortina SL3516 crypto engine, using `crypto_engine` serialization and software fallback for requests the descriptor engine cannot represent.

Important APIs and control flow: `sl3516_ce_skencrypt()` and `sl3516_ce_skdecrypt()` clear the request context, set operation direction, run `sl3516_ce_need_fallback()`, and either invoke `sl3516_ce_cipher_fallback()` or enqueue to `crypto_transfer_skcipher_request_to_engine()`. `sl3516_ce_handle_cipher_request()` is the engine callback and finalizes requests after `sl3516_ce_cipher()`. The hardware path maps source and destination SGs, converts each mapped segment into local `sginfo`, prepares `struct pkt_control_ecb` in coherent control memory, writes key material in big-endian word order, sets TQ flags for control/cipher/key descriptors, and calls `sl3516_ce_run_task()`. `sl3516_ce_aes_setkey()` validates 128/192/256-bit AES keys, stores a GFP_DMA copy for hardware, and sets the fallback key.

State and persistence behavior: per-TFM state stores the device pointer, fallback skcipher, key pointer, and key length. Per-request state stores mapped source/destination DMA addresses and lengths, operation direction, control packet length, TQ flags, pointer to the mutable cipher header, and fallback request. Device-level fallback counters record why requests could not use hardware: non-block length, SG count, 16-byte alignment, or mismatched source/destination lengths.

Dependencies and integration points: depends on `sl3516-ce.h` hardware descriptors, Linux skcipher and `crypto_engine`, DMA mapping, scatterlists, runtime PM held by TFM init/exit, and the single algorithm template in core for `ecb(aes)`. The cipher file does not register algorithms itself; core registration provides `sl3516_ce_cipher_init()`, `exit`, `setkey`, and encrypt/decrypt callbacks.

Risks and test signals: risks include strict fallback rules that reject valid skcipher requests unless every SG is 16-byte aligned and length-matched, possible DMA unmap on error paths before both sides are mapped, `MAXDESC` limiting source to three SGs because each source consumes a control descriptor plus data descriptor, hardware path only implementing ECB despite broader hardware capability, and key copies requiring correct byte order. Test signals include AES ECB known-answer tests for all key sizes, fallback tests for unaligned and odd-length SGs, DMA API debug under out-of-place errors, crypto_engine request ordering, runtime PM balance across TFM lifetime, and debugfs fallback counters changing as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-core.c

Purpose: provides the platform driver, descriptor-ring setup, DMA execution, interrupt handling, runtime PM, debugfs statistics, algorithm registration, and RNG registration for the SL3516 crypto engine.

Important APIs and control flow: `sl3516_ce_probe()` allocates `struct sl3516_ce_dev`, maps registers, requests the IRQ, obtains reset and clock, allocates coherent TX/RX descriptor rings plus one ECB control packet, initializes runtime PM, starts a `crypto_engine`, registers the AES skcipher template, registers the hwrng, resumes the device briefly to read IDs, and optionally creates debugfs stats. `sl3516_ce_desc_init()` builds circular TX and RX descriptor chains. `sl3516_ce_run_task()` fills RX descriptors for destination SGs, emits one control TX descriptor and one data TX descriptor per source SG, starts TX/RX DMA, waits up to five seconds for IRQ completion, and checks `IPSEC_STATUS_REG`. `ce_irq_handler()` acknowledges DMA status, logs bus/protocol errors, records TX/RX IRQ counters, and completes on RX EOF.

State and persistence behavior: persistent device state includes coherent descriptor memory, descriptor DMA addresses, current TX/RX indices, one coherent control packet, completion/status flags, crypto engine pointer, reset/clock handles, hwrng object, stats counters, and optional debugfs dentries. Runtime PM suspends by asserting reset and disabling the clock; resume enables the clock, deasserts reset, and restarts descriptor base registers.

Dependencies and integration points: depends on OF compatible `cortina,sl3516-crypto`, platform IRQ/MMIO resources, reset and clock providers, Linux DMA coherent allocation, `crypto_engine`, skcipher registration helpers, hwrng registration from `sl3516-ce-rng.c`, and shared hardware structures in `sl3516-ce.h`.

Risks and test signals: risks include only one in-flight task expected by shared completion/status and `crypto_engine` serialization, timeout path not resetting descriptors before later requests, descriptor ownership assumptions after errors, start registers being kicked inside each source SG loop, debugfs creation errors ignored, and probe unwind needing to unregister RNG, algorithms, engine, PM, and coherent memory in reverse order. Test signals include probe with valid DT resources, runtime suspend/resume around TFM use, IRQ RX EOF completion, deliberate DMA error logging, timeout recovery tests, debugfs counter reads, successful unregister on remove, and no DMA coherent leaks on probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-rng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-rng.c

Purpose: exposes the SL3516 crypto engine random-number register through the Linux hwrng framework.

Important APIs and control flow: `sl3516_ce_rng_register()` fills `ce->trng` with name, quality 700, and `sl3516_ce_rng_read()`, then calls `hwrng_register()`. `sl3516_ce_rng_read()` recovers `struct sl3516_ce_dev` via `container_of()`, optionally increments debug counters, runtime-resumes the device, repeatedly reads 32-bit words from `IPSEC_RAND_NUM_REG` until at least `max` bytes are produced, then releases runtime PM and returns the byte count. `sl3516_ce_rng_unregister()` calls `hwrng_unregister()`.

State and persistence behavior: state is embedded in `struct sl3516_ce_dev` as `struct hwrng trng` plus optional counters. No seed or entropy pool state is maintained by the driver; hardware register reads are direct. The function ignores the `wait` parameter and always performs immediate register reads after powering the device.

Dependencies and integration points: depends on runtime PM from core, the MMIO base and random register offset in `sl3516-ce.h`, and the Linux `hw_random` subsystem. Core probe registers the RNG after crypto algorithms and unregisters it first during remove/unwind.

Risks and test signals: risks include writing past `max` when `max` is not a multiple of four because the loop stores full `u32` words, no status/ready check before reading the random register, quality value being asserted without health tests in this file, and PM errors needing `pm_runtime_put_noidle()` as implemented. Test signals include hwrng registration, reads with non-multiple-of-four sizes under KASAN, runtime PM enable/disable tracing, repeated reads returning requested lengths, and debug counters matching hwrng activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce.h

Purpose: declares SL3516 crypto engine hardware constants, descriptor/control-packet layouts, device and request context structures, algorithm template type, and cross-file prototypes for the Gemini crypto driver.

Important APIs and control flow: register constants cover IPSEC identity/status, RNG, DMA status/control/current descriptor registers, and DMA device ID. Bit constants define TQ flags, descriptor first/last markers, DMA status interrupts/errors, TX/RX DMA control flags, and CPU/DMA ownership. `struct descriptor` models the CE network-like DMA descriptor with frame control, TX flag/status, buffer address, and next descriptor fields. `struct pkt_control_header`, `pkt_control_cipher`, and `pkt_control_ecb` model the control packet consumed by AES ECB. `struct sl3516_ce_dev` is the shared platform state; `struct sl3516_ce_cipher_req_ctx` is the skcipher request state; `struct sl3516_ce_cipher_tfm_ctx` is per-TFM state; `struct sl3516_ce_alg_template` wraps crypto algorithm registration and stats.

State and persistence behavior: the header owns no executable state, but fixes all persistent layouts shared between core, cipher, and RNG files. Device state includes MMIO, clock/reset, engine, completion, coherent descriptor rings, descriptor cursors, RNG object, stats, debugfs dentries, coherent control packet, and DMA addresses. Request state is bounded by `MAXDESC`, so SG capacity is part of the ABI.

Dependencies and integration points: depends on Crypto API AES/skcipher/engine types, scatterwalk, debugfs, hwrng, clock/reset/device types through users, and the SL3516 datasheet register format. Function prototypes connect core registration to cipher callbacks and RNG helpers.

Risks and test signals: risks include C bitfield layout depending on compiler and CPU endian assumptions, undocumented burst bits, `MAXDESC` being only six, comments with typoed fallback field names drifting from actual struct names, and broader hardware capabilities intentionally not represented. Test signals include descriptor byte layout matching hardware on target endian, successful circular descriptor chaining, correct AES key-size encoding through `aesnk`, compile coverage with and without debug config, and no request context overflow for maximum accepted SG counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/gemini/sl3516-ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/geode-aes.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/geode-aes.c

Purpose: implements the AMD Geode LX PCI AES hardware driver. It registers a legacy single-block `aes` cipher plus kernel-driver-only `cbc(aes)` and `ecb(aes)` skcipher algorithms, using hardware only for 128-bit AES keys and falling back to software for 192/256-bit keys.

Important APIs and control flow: PCI probe enables the device, requests BAR regions, maps BAR0, clears pending AES interrupts, registers `geode_alg`, then registers the skcipher algorithms. `_writefield()` and `_readfield()` transfer 128-bit key/IV fields. `do_crypt()` writes physical source/destination addresses, length, and control flags, starts the engine, polls `AES_INTR_REG` until `AES_INTRA_PENDING`, clears the event, and reports timeout. `geode_aes_crypt()` serializes hardware access with a global spinlock, sets CBC/encrypt/write-key flags, writes IV and key, calls `do_crypt()`, BUGs on timeout, and reads back the updated CBC IV. Cipher and skcipher setkey paths store 128-bit keys locally or configure fallback transforms for unsupported key sizes. `geode_skcipher_crypt()` walks virtual skcipher segments and calls hardware per block-aligned chunk.

State and persistence behavior: global `_iobase` and `lock` mean one mapped hardware engine and serialized operations. Per-TFM state stores a 128-bit hardware key, fallback cipher/skcipher, and key length. CBC IV state is updated in the caller's walk IV by reading the hardware IV register after each chunk. PCI remove unregisters algorithms, unmaps I/O, releases regions, and disables the device.

Dependencies and integration points: depends on PCI ID `PCI_DEVICE_ID_AMD_LX_AES`, MMIO register definitions from `geode-aes.h`, Linux Crypto API cipher/skcipher internals, `skcipher_walk_virt()`, fallback algorithm allocation, and `virt_to_phys()` addressing for buffers supplied by the walk.

Risks and test signals: risks include `BUG_ON(ret)` on hardware timeout, use of `virt_to_phys()` instead of DMA mapping, global state preventing multiple devices, hardware path limited to AES-128, legacy cipher API exposure, polling under spinlock with IRQs disabled, and driver-only skcipher flags limiting generic selection. Test signals include PCI probe/remove, Crypto API KATs for AES-128 ECB/CBC hardware and 192/256 fallback, CBC IV propagation across multi-segment walks, timeout/error injection, lockdep coverage for spinlocked polling, and DMA/cache-coherency validation on Geode LX hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/geode-aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/geode-aes.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/geode-aes.h

Purpose: defines the private register map, control bits, mode/direction constants, timeout value, and per-TFM context for the AMD Geode LX AES driver.

Important APIs and control flow: mode constants identify ECB and CBC, direction constants distinguish encrypt and decrypt, and register offsets name control, interrupt, source, destination, length, write-key, and write-IV registers. Control bits start an operation, select encryption, request key write, set coherent source/destination access, and enable CBC. Interrupt bits identify pending AES channel events and clear/mask state. `AES_OP_TIMEOUT` bounds the driver's polling loop. `struct geode_aes_tfm_ctx` stores the hardware AES-128 key, either a fallback `crypto_skcipher` or legacy `crypto_cipher`, and the active key length.

State and persistence behavior: the header itself has no runtime state. It defines how `geode-aes.c` persists per-TFM key/fallback state and how MMIO offsets are interpreted. The hardware key and IV registers are transient and rewritten for each operation.

Dependencies and integration points: depends on AES key-size constants and Crypto API fallback types included by the C file. Its register constants are consumed directly by MMIO reads/writes and must match the AMD LX AES BAR layout.

Risks and test signals: risks include incorrect register constants causing data corruption, timeout tuning hiding hung hardware or false failures, an unused hidden-key flag, and context union misuse if cipher and skcipher init paths are mixed. Test signals include compile coverage for both legacy cipher and skcipher users, register access traces on known hardware, fallback allocation and free for both union variants, and AES-128 hardware results matching software for ECB and CBC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/geode-aes.h -->
