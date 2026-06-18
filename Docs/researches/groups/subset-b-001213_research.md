# subset-b-001213 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-core.c

## Purpose

`sun8i-ce-core.c` is the platform, capability, queue, interrupt, runtime-PM, and CryptoAPI registration layer for the Allwinner Crypto Engine used by H3/R40/D1/A64/H5/H6/H616-class SoCs. It selects a `ce_variant` from device tree, registers supported skcipher, ahash, RNG, and optional hwrng algorithms, and provides the shared descriptor execution helper used by cipher, hash, PRNG, and TRNG files.

## Important APIs, Types, And Functions

The central routines are `sun8i_ce_probe()`, `sun8i_ce_remove()`, `sun8i_ce_register_algs()`, `sun8i_ce_unregister_algs()`, `sun8i_ce_allocate_chanlist()`, `sun8i_ce_get_engine_number()`, `sun8i_ce_run_task()`, and `ce_irq_handler()`. Static `ce_variant` records encode per-SoC algorithm IDs, error-register layout, clock requirements, byte/word length quirks, word-address descriptors, PRNG/TRNG support, and clock limits. `ce_algs[]` provides CryptoAPI templates for AES/DES3 ECB/CBC, MD5/SHA* hashes, and `stdrng`.

## Control Flow

Probe allocates `sun8i_ce_dev`, maps MMIO, resolves clocks, IRQ, and reset, creates four flow engines with one coherent `ce_task` descriptor each, enables runtime PM, requests the non-secure IRQ, registers algorithms, resumes once to read the die ID and register the optional TRNG, then optionally creates debugfs stats. Crypto requests choose a flow round-robin except flow 3, which is reserved for xRNG users. `sun8i_ce_run_task()` enables the flow interrupt, writes the task descriptor address to `CE_TDQ`, starts execution via `CE_TLR`, waits for IRQ completion, and decodes variant-specific `CE_ESR` error bits.

## State And Persistence Behavior

Persistent runtime state is held in `sun8i_ce_dev`: MMIO base, clocks, reset, mutexes, flow array, round-robin atomic, variant pointer, debugfs dentries, and optional hwrng counters. Each `sun8i_ce_flow` persists its crypto engine, completion, status, coherent descriptor pointer, and physical address. Runtime PM asserts reset and disables clocks on suspend; resume re-enables declared clocks and deasserts reset. Registered TFMs hold runtime PM references through their init/exit paths.

## Dependencies And Integration Points

The file integrates with platform/OF matching, common clock/reset, runtime PM autosuspend, IRQs, DMA coherent allocation, debugfs, `crypto_engine`, internal skcipher/hash/rng registration helpers, and optional `hwrng`. Device-tree compatibles select exact variant behavior, so SoC data is part of the hardware ABI.

## Risks And Test Signals

Risks include wrong variant tables, H3 clock tuning regressions, error-register bit slicing mistakes, descriptor address-size quirks on H616, missing unwind for partially registered algorithms, RNG flow contention, and DMA timeouts hidden until real storage workloads. Test with CryptoAPI selftests plus LUKS or dm-crypt IO, per-compatible probe/remove, runtime PM suspend/resume, debugfs fallback counters, PRNG/TRNG registration, IRQ completion, and fault injection around `CE_ESR` and clock/reset failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-hash.c

## Purpose

`sun8i-ce-hash.c` implements one-shot hardware acceleration for MD5, SHA1, SHA224, SHA256, SHA384, and SHA512 on the Allwinner CE while delegating streaming `init/update/final/finup/export/import` and unsupported request shapes to fallback ahash implementations.

## Important APIs, Types, And Functions

Key entry points are `sun8i_ce_hash_init_tfm()`, `sun8i_ce_hash_exit_tfm()`, `sun8i_ce_hash_init()`, `sun8i_ce_hash_update()`, `sun8i_ce_hash_final()`, `sun8i_ce_hash_finup()`, `sun8i_ce_hash_digest()`, and `sun8i_ce_hash_run()`. Hardware preparation is split across `sun8i_ce_hash_need_fallback()`, `hash_pad()`, `sun8i_ce_hash_prepare()`, and `sun8i_ce_hash_unprepare()`. The request context stores fallback request storage, selected flow, mapped SG count, result/pad DMA addresses, aligned result buffer, and two-block padding buffer.

## Control Flow

TFM init allocates a fallback ahash with `CRYPTO_ALG_NEED_FALLBACK`, mirrors its state size, sets request size with DMA padding, records debug fallback name, and holds a runtime PM reference. `digest()` rejects zero-length, too-many-SG, unaligned, or non-word-length source requests to fallback; otherwise it selects a CE flow and queues the request to that flow's `crypto_engine`. The engine callback maps source SGs, maps an internal result buffer, builds software MD/SHA padding as an extra source segment, fills `ce_task` source/destination descriptors and length units, runs `sun8i_ce_run_task()`, unmaps DMA resources, copies the digest to `areq->result`, and finalizes the hash request.

## State And Persistence Behavior

The hardware path is stateless per digest request except for flow selection and per-request DMA mappings. Streaming hash state is entirely owned by the fallback ahash. Runtime PM lifetime is tied to hash TFM allocation, not individual digest operations. Debug builds accumulate request and fallback counters in the shared algorithm template.

## Dependencies And Integration Points

This file depends on the CE core for variant algorithm IDs, length-unit quirks, flow engines, descriptor address conversion, and task execution. It uses Linux ahash internals, scatterlists, DMA mapping, SHA/MD5 constants, and local bottom-half disabling around CryptoAPI completion.

## Risks And Test Signals

Risks include padding overflow, SHA224/SHA384 digest-size normalization errors, incorrect bit-vs-word `t_dlen` on H6-like variants, insufficient fallback for malformed SGs, DMA map/unmap imbalance, and assumptions that all source SG lengths are word multiples. Test zero-length and misaligned fallback, all digest algorithms and sizes, multi-SG boundaries near padding-block transitions, H6 length-bit behavior, runtime PM TFM lifetime, and CryptoAPI hash selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-prng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-prng.c

## Purpose

`sun8i-ce-prng.c` exposes the CE pseudo-random generator as the CryptoAPI `stdrng` implementation registered by the core file. It manages caller-provided seed storage, programs the dedicated xRNG flow, and updates the seed from generated output.

## Important APIs, Types, And Functions

The file exports `sun8i_ce_prng_init()`, `sun8i_ce_prng_exit()`, `sun8i_ce_prng_seed()`, and `sun8i_ce_prng_generate()`. It uses `struct sun8i_ce_rng_tfm_ctx` for seed pointer and length, `struct ce_task` for the hardware descriptor, and `ce->rnglock` to serialize use of flow 3.

## Control Flow

Init zeroes the RNG context. Seed replaces or allocates a sensitive GFP_DMA seed buffer and records the length. Generate refuses unseeded use, rounds requested output plus seed material to a PRNG block multiple, allocates a DMA-capable bounce output buffer, maps seed and destination, resumes the device, locks `rnglock`, fills a flow-3 task with PRNG algorithm ID, key/IV seed pointers, destination SG, and variant-specific byte/word `t_dlen`, runs `sun8i_ce_run_task()`, unlocks and drops runtime PM, then copies requested bytes to the caller and refreshes the seed from subsequent output bytes.

## State And Persistence Behavior

Seed bytes persist in the TFM context until reseed or exit and are freed with `kfree_sensitive()`. Hardware state is not persisted outside each descriptor execution. Flow 3 is a shared CE resource guarded by `rnglock`, so PRNG and TRNG serialize with each other.

## Dependencies And Integration Points

It depends on the core algorithm template for device lookup, variant PRNG algorithm IDs, task execution, runtime PM, DMA mapping, and CryptoAPI RNG callbacks. `PRNG_SEED_SIZE`, `PRNG_DATA_SIZE`, and `PRNG_LD` are defined in `sun8i-ce.h`.

## Risks And Test Signals

Risks include accepting unexpected seed lengths, output rounding mistakes, seed refresh overlap, DMA mapping failures, lack of per-request use of the `src/slen` generate arguments, and contention with TRNG on flow 3. Test unseeded failure, reseed with changed lengths, various output lengths around PRNG block size, rngtest quality, runtime PM transitions, and concurrent RNG users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-prng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-trng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-trng.c

## Purpose

`sun8i-ce-trng.c` registers the CE true random generator with the kernel hwrng framework when the selected variant advertises TRNG support. It supports both old and v2 TRNG algorithm IDs, with comments noting that only the second generation is reliable under rngtest.

## Important APIs, Types, And Functions

The main callbacks are `sun8i_ce_trng_read()`, `sun8i_ce_hwrng_register()`, and `sun8i_ce_hwrng_unregister()`. The read path programs a `ce_task` on flow 3, uses `ce->trng.read` as the hwrng callback, and records optional debug counters on `sun8i_ce_dev`.

## Control Flow

Register returns early when the variant has `CE_ID_NOTSUPP`; otherwise it names the hwrng and calls `hwrng_register()`. Reads round the requested byte count to a 32-byte multiple, allocate a sensitive DMA-capable buffer, map it for device output, resume the CE, lock `rnglock`, build a TRNG task descriptor with variant-specific length units and one destination segment, execute flow 3, unlock and drop runtime PM, copy exactly `max` bytes to the hwrng buffer on success, and return the byte count.

## State And Persistence Behavior

No per-consumer state is stored. Hardware execution is per read and serialized by `rnglock` with PRNG. The hwrng registration object lives inside `sun8i_ce_dev` and is unregistered during core driver removal.

## Dependencies And Integration Points

It integrates with the CE core variant table, `sun8i_ce_run_task()`, runtime PM, DMA mapping, Linux hwrng, and optional debug counters. Registration is called from `sun8i_ce_probe()` only after the device has been runtime-resumed.

## Risks And Test Signals

Risks include exposing unreliable first-generation TRNG variants, returning `-ENOMEM` from hwrng read paths under pressure, length unit mismatches, flow-3 contention with PRNG, and ignoring the hwrng `wait` argument. Test hwrng registration on TRNG and non-TRNG compatibles, `rngtest` quality on H6/D1/H616, short and long reads, concurrent RNG access, runtime PM, and remove/unregister sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce.h

## Purpose

`sun8i-ce.h` is the shared interface and hardware contract for the Allwinner CE driver. It defines register offsets, algorithm/control bits, error bits, descriptor layout, SoC variant description, device/flow/request/TFM state, address conversion helpers, and cross-file function prototypes.

## Important APIs, Types, And Functions

Important types include `struct ce_variant`, `struct ce_task`, `struct sginfo`, `struct sun8i_ce_flow`, `struct sun8i_ce_dev`, `struct sun8i_cipher_req_ctx`, `struct sun8i_cipher_tfm_ctx`, `struct sun8i_ce_hash_tfm_ctx`, `struct sun8i_ce_hash_reqctx`, `struct sun8i_ce_rng_tfm_ctx`, and `struct sun8i_ce_alg_template`. `desc_addr_val()` and `desc_addr_val_le32()` abstract H616-style word addresses. Prototypes connect the core, cipher, hash, PRNG, and TRNG implementation files.

## Control Flow

The header itself has no runtime flow, but it defines the descriptor and state fields consumed by all runtime paths: core code allocates flows and descriptors, cipher/hash fill `ce_task` source/destination entries, PRNG/TRNG use flow 3, and all paths call `sun8i_ce_run_task()`. Variant flags influence descriptor address encoding and length units.

## State And Persistence Behavior

The structures define all persistent driver state: device-level clocks/reset/MMIO/debug/hwrng state, per-flow completions and coherent descriptor memory, TFM-level keys or fallback TFMs, request-level DMA mappings, and RNG seed storage. Descriptor layout is packed and aligned to the hardware ABI.

## Dependencies And Integration Points

The header integrates CryptoAPI AES/DES/skcipher/hash/rng headers, debugfs, hwrng, atomics, and SHA/MD5 constants. Its constants bind driver code to CE register semantics, supported algorithm IDs, maximum scatterlist count, clock count, DMA timeout, and flow count.

## Risks And Test Signals

Risks include ABI drift in packed descriptor layout, wrong enum indexes into variant capability arrays, mismatched comments (`hash_t_dlen_in_bytes` vs `hash_t_dlen_in_bits`), address conversion mistakes for word-address SoCs, and request context sizing around fallback objects. Test by building all CE config combinations, running sparse/clang structure layout checks, exercising every variant flag, and verifying DMA descriptors against hardware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/Makefile

## Purpose

This Makefile builds the Allwinner sun8i Security System module from the core and cipher objects, with optional PRNG and hash objects selected by Kconfig symbols.

## Important APIs, Types, And Functions

It declares `obj-$(CONFIG_CRYPTO_DEV_SUN8I_SS) += sun8i-ss.o`, always includes `sun8i-ss-core.o` and `sun8i-ss-cipher.o`, and conditionally adds `sun8i-ss-prng.o` and `sun8i-ss-hash.o`.

## Control Flow

There is no runtime control flow. Build-time selection determines whether the module exports only skcipher algorithms or also the `stdrng` and ahash/HMAC templates registered by the core file.

## State And Persistence Behavior

No runtime state is stored here. The build state persists in the generated composite object and controls which code paths are linked into the module.

## Dependencies And Integration Points

It integrates with kbuild and the `CONFIG_CRYPTO_DEV_SUN8I_SS*` symbols. The conditional object list must match prototypes and algorithm templates in `sun8i-ss-core.c` and `sun8i-ss.h`.

## Risks And Test Signals

Risks include unresolved symbols if optional object selections do not align with core template `#ifdef`s, and missing features when Kconfig enables an algorithm but the object is not linked. Test all combinations of base, PRNG, and hash config symbols with module and built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-cipher.c

## Purpose

`sun8i-ss-cipher.c` implements AES and 3DES ECB/CBC skcipher acceleration for the Allwinner A80/A83T Security System, using fallback skcipher providers for shapes the SS DMA engine cannot process.

## Important APIs, Types, And Functions

Key functions are `sun8i_ss_need_fallback()`, `sun8i_ss_cipher_fallback()`, `sun8i_ss_setup_ivs()`, `sun8i_ss_cipher()`, `sun8i_ss_handle_cipher_request()`, `sun8i_ss_skencrypt()`, `sun8i_ss_skdecrypt()`, `sun8i_ss_cipher_init()`, `sun8i_ss_cipher_exit()`, `sun8i_ss_aes_setkey()`, and `sun8i_ss_des3_setkey()`.

## Control Flow

Encrypt/decrypt zero the request context, set direction, reject zero or non-16-byte lengths, too many SGs, unaligned offsets, non-16-byte SG chunks, and mismatched source/destination SG layouts to fallback. Hardware requests select a flow, queue to that flow's crypto engine, map the key and optional IVs, map source/destination SGs, translate each segment into `t_src`/`t_dst` word lengths, and call `sun8i_ss_run_task()`. CBC IV handling precomputes per-SG IVs for decrypt and updates the caller IV from the last ciphertext block or saved decrypt IV.

## State And Persistence Behavior

TFM state stores the key, key length, SS device, and fallback TFM. Request state stores mapped source/destination entries, key and IV DMA addresses, method, mode, direction, flow, and fallback request. Per-flow IV and backup buffers are allocated by the core and scrubbed after use.

## Dependencies And Integration Points

It depends on `sun8i-ss-core.c` for engine queues, register programming, runtime PM references held by TFM init, and algorithm templates. It uses scatterwalk helpers, DMA mapping, skcipher internals, and fallback algorithm registration through `CRYPTO_ALG_NEED_FALLBACK`.

## Risks And Test Signals

Risks include stale `rctx->niv` causing IV unmap issues, exact SG-layout constraints pushing many users to fallback, IV update mistakes for in-place decrypt, key DMA lifetime errors, and hardware length units in words. Test AES/3DES ECB/CBC known vectors, in-place and out-of-place CBC, multi-SG boundaries, fallback counters, invalid key lengths, unaligned buffers, and concurrent two-flow operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-core.c

## Purpose

`sun8i-ss-core.c` is the platform driver and registration layer for the older Allwinner Security System crypto block found on A80/A83T. It owns SoC variant capability data, flow allocation, register-level task execution, IRQ handling, runtime PM, debugfs stats, and CryptoAPI algorithm registration.

## Important APIs, Types, And Functions

Important functions are `sun8i_ss_probe()`, `sun8i_ss_remove()`, `sun8i_ss_register_algs()`, `sun8i_ss_unregister_algs()`, `allocate_flows()`, `sun8i_ss_get_engine_number()`, `sun8i_ss_run_task()`, `ss_irq_handler()`, `sun8i_ss_pm_resume()`, and `sun8i_ss_pm_suspend()`. `ss_a80_variant` supports ciphers only; `ss_a83t_variant` adds MD5/SHA1/SHA224/SHA256.

## Control Flow

Probe allocates `sun8i_ss_dev`, maps MMIO, gets clocks, IRQ, reset, allocates two flows and their helper buffers, initializes runtime PM, requests IRQ, registers supported algorithms, resumes once to read the die ID, and optionally creates debugfs. `sun8i_ss_run_task()` serializes register access with `mlock`, writes key/IV/source/destination/length registers per destination segment, starts the selected flow, and waits for the flow completion signaled by `ss_irq_handler()`.

## State And Persistence Behavior

Device state stores base, clocks, reset, mutex, flow array, round-robin atomic, variant pointer, and optional debugfs dentries. Each flow persists a crypto engine, completion, status, per-SG IV buffers, backup IV, hash pad/result buffers, and optional request count. Runtime suspend asserts reset and disables clocks; resume enables clocks, deasserts reset, and enables flow interrupts.

## Dependencies And Integration Points

It integrates with OF platform matching, common clock/reset, runtime PM, IRQs, `crypto_engine`, skcipher/hash/rng registration, DMA-capable helper buffers, and debugfs. Algorithm templates reference functions from cipher, hash, and PRNG files conditionally linked by the Makefile.

## Risks And Test Signals

Risks include register serialization blocking both flows, incomplete runtime PM unwind, optional algorithm symbols mismatching config, flow buffers sized for hash/HMAC assumptions, and timeout handling returning only `-EFAULT`. Test A80 vs A83T capability filtering, module remove with active TFMs, runtime suspend/resume, IRQ completion per flow, debugfs stats, and all optional build combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-hash.c

## Purpose

`sun8i-ss-hash.c` accelerates one-shot MD5/SHA1/SHA224/SHA256 and HMAC-SHA1 on A83T Security System hardware, while forwarding streaming ahash operations and unsupported request layouts to fallback implementations.

## Important APIs, Types, And Functions

Key functions are `sun8i_ss_hash_init_tfm()`, `sun8i_ss_hash_exit_tfm()`, `sun8i_ss_hmac_setkey()`, `sun8i_ss_hashkey()`, `sun8i_ss_hash_need_fallback()`, `sun8i_ss_hash_digest()`, `hash_pad()`, `sun8i_ss_run_hash_task()`, and `sun8i_ss_hash_run()`. TFM state stores fallback ahash, device pointer, HMAC ipad/opad, and normalized key.

## Control Flow

TFM init allocates fallback ahash, sets state/request sizes, records fallback name, and resumes the device. Streaming callbacks configure and call fallback. One-shot digest rejects zero length, too-large requests for the fixed pad buffer, too many SGs, non-final partial blocks, unaligned offsets, and non-word SG lengths. The engine callback maps source SGs, maps a per-flow result buffer, copies the final partial block into the flow pad buffer, appends MD/SHA padding, and runs the hardware. For HMAC, it first shifts SG entries to prepend `ipad`, runs the inner digest, then retries with `opad || inner_digest`.

## State And Persistence Behavior

Request state contains source/destination descriptor arrays, selected method, flow, and fallback request. Per-flow pad and result buffers are reused. HMAC key material persists in TFM context until exit and is freed with sensitive cleanup for pads. Hardware hash state is passed between multi-SG chunks by using the previous result as key/IV and setting continuation bit `BIT(17)`.

## Dependencies And Integration Points

It depends on core flow buffers, `sun8i_ss_run_hash_task()`, CryptoAPI ahash/HMAC helpers, SHA/MD5 constants, scatterwalk, DMA mapping, and runtime PM acquired at TFM lifetime. It registers through hash templates in `sun8i-ss-core.c`.

## Risks And Test Signals

Risks include `sg_nents()` not bounded by request length, fixed 4096-byte pad buffer limits, HMAC allocation leaks on repeated setkey, digest-size normalization for SHA224, and complex map/unmap retry flow for HMAC. Test hash vectors, HMAC-SHA1 vectors with long keys, final partial block handling, maximum accepted length, fallback counters, DMA map failure paths, and multi-SG continuation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-prng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-prng.c

## Purpose

`sun8i-ss-prng.c` exposes the Security System PRNG as CryptoAPI `stdrng`. It stores seed material in the RNG TFM, programs SS PRNG registers directly, and refreshes the seed from extra generated bytes because the hardware does not return an updated seed separately.

## Important APIs, Types, And Functions

The file exports `sun8i_ss_prng_seed()`, `sun8i_ss_prng_init()`, `sun8i_ss_prng_exit()`, and `sun8i_ss_prng_generate()`. It uses `struct sun8i_ss_rng_tfm_ctx`, SS PRNG control bits, flow completion state, and the shared device mutex.

## Control Flow

Generate verifies the TFM is seeded, rounds requested output plus new seed material to a PRNG block multiple and DMA cache alignment, allocates a bounce buffer, chooses a flow, maps seed and destination, resumes the device, locks `mlock`, writes IV, key, destination, length, and control registers, waits for flow completion with a timeout proportional to output size, unlocks, drops runtime PM, unmaps DMA resources, copies requested bytes to the caller, and replaces the seed from following output bytes.

## State And Persistence Behavior

Seed material persists in the TFM and is freed with `kfree_sensitive()` on exit or reseed. The PRNG path uses the global `mlock` until hardware completion, intentionally blocking cipher/hash users on both flows to prevent collisions because RNG is not routed through `crypto_engine`.

## Dependencies And Integration Points

It depends on the core registration template, runtime PM, flow IRQ completion, DMA mapping, and direct SS register programming. The Makefile links it only when `CONFIG_CRYPTO_DEV_SUN8I_SS_PRNG` is enabled.

## Risks And Test Signals

Risks include full-device serialization during generation, timeout scaling with requested length, seed-size assumptions, PRNG quality sensitivity to writing both IV and key registers, and ignored `src/slen` generate parameters. Test unseeded generation, reseed, odd lengths, concurrent cipher plus RNG, rngtest quality, runtime PM, and large outputs near timeout limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-prng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss.h

## Purpose

`sun8i-ss.h` defines the shared register constants, algorithm bits, flow limits, state structures, algorithm templates, and cross-file prototypes for the Allwinner A80/A83T Security System driver.

## Important APIs, Types, And Functions

Important definitions include `SS_CTL_REG`, `SS_INT_*`, `SS_KEY_ADR_REG`, `SS_IV_ADR_REG`, `SS_SRC_ADR_REG`, `SS_DST_ADR_REG`, `SS_LEN_ADR_REG`, algorithm/mode constants, `MAXFLOW`, `MAX_SG`, and `MAX_PAD_SIZE`. Important types are `struct ss_variant`, `struct sginfo`, `struct sun8i_ss_flow`, `struct sun8i_ss_dev`, cipher/hash/RNG TFM and request contexts, and `struct sun8i_ss_alg_template`.

## Control Flow

The header has no direct runtime execution, but it defines the data contract: core code allocates `sun8i_ss_flow`, cipher/hash/PRNG populate request contexts, and all hardware users coordinate through the shared register offsets and flow state.

## State And Persistence Behavior

Persistent state includes device MMIO/clock/reset/flow/debug state, per-flow IV/pad/result buffers, cipher keys and fallback TFMs, hash fallback and HMAC pad/key material, and RNG seed material. Many structures hold DMA addresses or word-count lengths consumed by hardware.

## Dependencies And Integration Points

It integrates CryptoAPI AES/DES/skcipher/rng/hash headers, debugfs, atomics, scatterlists, MD5/SHA constants, and driver-internal function prototypes. It is included by all SS implementation files and must stay aligned with conditional object linkage.

## Risks And Test Signals

Risks include fixed limits that shape fallback behavior, missing include guards, packed hardware assumptions in plain `struct sginfo`, request context layout with fallback request at the end, and state fields shared across optional build configurations. Test all config combinations, structure-size expectations, fallback request sizing, and sparse/compile warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/amcc/Makefile

## Purpose

This Makefile builds the AMCC/PPC4xx crypto accelerator module and conditionally links the PPC4xx TRNG hwrng support.

## Important APIs, Types, And Functions

It declares `obj-$(CONFIG_CRYPTO_DEV_PPC4XX) += crypto4xx.o`, combines `crypto4xx_core.o` and `crypto4xx_alg.o`, and appends `crypto4xx_trng.o` when `CONFIG_HW_RANDOM_PPC4XX` is enabled.

## Control Flow

There is no runtime control flow. Build-time object selection decides whether `ppc4xx_trng_probe()` and `ppc4xx_trng_remove()` are real functions or inline no-ops from the header.

## State And Persistence Behavior

No runtime state is stored. The built composite object determines which algorithms and optional hwrng code are present.

## Dependencies And Integration Points

It integrates with kbuild and the `CRYPTO_DEV_PPC4XX` and `HW_RANDOM_PPC4XX` symbols. It must align with `crypto4xx_trng.h` conditional prototypes and calls from `crypto4xx_core.c`.

## Risks And Test Signals

Risks include optional TRNG linkage mismatch and missing core or algorithm symbols. Test base driver builds with and without hwrng, module and built-in builds, and link-time symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_alg.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_alg.c

## Purpose

`crypto4xx_alg.c` implements CryptoAPI algorithm operations for the AMCC/PPC4xx crypto engine. It builds dynamic Security Associations for AES ECB/CBC/CTR/RFC3686 and AEAD CCM/GCM, invokes packet-descriptor submission in the core file, and uses software fallbacks for hardware edge cases.

## Important APIs, Types, And Functions

Key helpers are `set_dynamic_sa_command_0()`, `set_dynamic_sa_command_1()`, `crypto4xx_crypt()`, `crypto4xx_setkey_aes()`, `crypto4xx_setkey_aes_{cbc,ecb,ctr}()`, `crypto4xx_setkey_rfc3686()`, `crypto4xx_ctr_crypt()`, `crypto4xx_aead_need_fallback()`, `crypto4xx_aead_fallback()`, `crypto4xx_setkey_aes_ccm()`, `crypto4xx_crypt_aes_ccm()`, `crypto4xx_setkey_aes_gcm()`, and `crypto4xx_crypt_aes_gcm()`.

## Control Flow

Setkey routines allocate inbound/outbound SA buffers, fill command words, key fields, key lengths, mode bits, and AEAD hash state. Encrypt/decrypt entry points build IV words, choose inbound or outbound SA, and call `crypto4xx_build_pd()`. CTR falls back if the 32-bit hardware counter would overflow while Linux expects full-IV carry. AEAD falls back when auth size is not word aligned, plaintext is shorter than one AES block, associated data is unaligned or over 1020 bytes, or CCM counter length is unsupported.

## State And Persistence Behavior

TFM state is in `struct crypto4xx_ctx`: device pointer, inbound/outbound SA buffers, SA length, RFC3686 nonce, and fallback cipher/AEAD. Per-request state is mostly supplied to the core packet descriptor builder. GCM computes the GHASH subkey in software during setkey and stores it inside the SA.

## Dependencies And Integration Points

It depends on `crypto4xx_core.c` for descriptor submission, `crypto4xx_sa.h` for dynamic SA layout, `crypto4xx_core.h` endian-copy helpers, AES/CTR/GCM/AEAD CryptoAPI headers, and fallback algorithms configured by core algorithm registration.

## Risks And Test Signals

Risks include SA bitfield mistakes, endian conversion errors in key/IV/hash subkey fields, AEAD fallback boundary regressions, CCM nonce-length handling, auth tag placement/checking across core completion, and use of stack temporary SAs in asynchronous submission. Test AES mode vectors, RFC3686 nonce handling, CTR overflow fallback, CCM/GCM vectors with multiple auth sizes and assoc lengths, short plaintext fallback, and key-size rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_alg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_core.c

## Purpose

`crypto4xx_core.c` is the platform driver, descriptor-ring manager, interrupt/tasklet completion engine, algorithm registrar, and PRNG provider for AMCC/PPC4xx crypto hardware.

## Important APIs, Types, And Functions

Important functions include `crypto4xx_probe()`, `crypto4xx_remove()`, `crypto4xx_hw_init()`, `crypto4xx_build_{pdr,gdr,sdr}()`, descriptor get/put helpers, `crypto4xx_build_pd()`, `crypto4xx_cipher_done()`, `crypto4xx_aead_done()`, `crypto4xx_bh_tasklet_cb()`, interrupt handlers, `crypto4xx_register_alg()`, `crypto4xx_unregister_alg()`, `crypto4xx_sk_init()`, `crypto4xx_aead_init()`, and `crypto4xx_prng_generate()`. `crypto4xx_alg[]` registers AES skciphers, CCM/GCM AEAD, and `stdrng`.

## Control Flow

Probe resets supported PPC405EX/460EX/460SX crypto blocks through DCR registers, detects revision quirks, allocates core/device state, initializes locks and ratelimit, allocates SDR/PDR/GDR rings plus shadow SA/state pools, maps MMIO, requests IRQ, initializes hardware registers, registers algorithms, and probes optional TRNG. Request submission reserves contiguous gather/scatter/packet descriptors under spinlock, copies the requested SA into the packet's shadow SA, inserts IV and state-record pointers, maps source/destination or sets scatter buffers, marks the PD host-ready, and rings `CRYPTO4XX_INT_DESCR_RD`. IRQ clears status and schedules the tasklet; the tasklet walks completed PDs from tail, calls cipher or AEAD completion, frees ring descriptors, and completes CryptoAPI requests.

## State And Persistence Behavior

Persistent device state includes PDR/GDR/SDR rings, scatter bounce buffers, shadow SA and state-record pools, ring heads/tails, per-PD metadata, registered algorithm list, revision flag, PRNG/TRNG bases, locks, tasklet, IRQ, and hwrng pointer. Packet descriptors own temporary mappings until completion. PRNG generation reads hardware PRNG registers under `rng_lock`; seed callback is a no-op because hardware is seeded in `crypto4xx_hw_init()`.

## Dependencies And Integration Points

The file integrates OF platform probing, PowerPC DCR reset registers, DMA coherent/page mapping, scatterwalk, CryptoAPI skcipher/AEAD/RNG registration, tasklets, IRQs, optional TRNG, and AMCC-specific register/SA headers. Algorithm operations in `crypto4xx_alg.c` are thin wrappers over `crypto4xx_build_pd()`.

## Risks And Test Signals

Risks include descriptor-ring wrap bugs, DMA map leaks on partial setup failure, source mappings not explicitly unmapped in visible completion paths, `crypto4xx_get_n_sd()` comparing against `gdr_tail`, interrupt coalescing revision handling, AEAD tag copy/check offsets, busy/backlog return semantics, and optional TRNG lifetime. Test high-concurrency dm-crypt/IPsec workloads, ring exhaustion/backlog behavior, SG wrap-around, AEAD error tags, module remove, interrupt coalescing on RevA/RevB, PRNG reads, and DMA API debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_core.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_core.h

## Purpose

`crypto4xx_core.h` defines the shared state, ring sizes, descriptor metadata, context structures, prototypes, and endian-copy helpers for the PPC4xx crypto driver.

## Important APIs, Types, And Functions

Key definitions include ring sizes (`PPC4XX_NUM_PD/GD/SD`), descriptor states, reset constants, `union shadow_sa_buf`, `struct pd_uinfo`, `struct crypto4xx_device`, `struct crypto4xx_core_device`, `struct crypto4xx_ctx`, `struct crypto4xx_aead_reqctx`, `struct crypto4xx_alg_common`, and `struct crypto4xx_alg`. It declares `crypto4xx_build_pd()`, SA allocation/free, AES/AEAD operations, and endian helpers `crypto4xx_memcpy_{to,from}_le32()`.

## Control Flow

The header has no standalone runtime flow. It defines how algorithm code calls core packet submission and how core code tracks rings, requests, algorithm registration, PRNG/TRNG integration, and fallback cipher state.

## State And Persistence Behavior

Persistent state includes ring memory, ring heads/tails, shadow SA/state pools, per-PD async request metadata, algorithm list, ratelimit state, revision flag, hwrng pointer, tasklet, spinlock, and RNG mutex. `struct crypto4xx_ctx` persists per TFM SA buffers and fallback algorithm handles.

## Dependencies And Integration Points

It includes CryptoAPI internal skcipher/AEAD/RNG headers, scatterlists, mutexes, ratelimit, and the driver register/SA headers. The GCC access attribute on `crypto4xx_build_pd()` helps static checking of IV buffer length.

## Risks And Test Signals

Risks include fixed ring sizes and 256-byte shadow SA pool assumptions, packed SA aliasing, endian helper use on unaligned buffers, missing source DMA fields in `pd_uinfo`, and context union misuse between skcipher and AEAD. Test compile with GCC/Clang, sparse, DMA API debugging, all algorithm init/exit paths, and high descriptor pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_reg_def.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_reg_def.h

## Purpose

`crypto4xx_reg_def.h` is the PPC4xx crypto-engine register and descriptor ABI header. It defines MMIO offsets, interrupt bits, PRNG registers, DMA/ring configuration values, gather/scatter descriptor formats, and packet descriptor formats.

## Important APIs, Types, And Functions

Important definitions include `CRYPTO4XX_*` register offsets, interrupt masks such as `CRYPTO4XX_INT_PDR_DONE` and `CRYPTO4XX_INT_ERROR`, PRNG status/control/result registers, `PPC4XX_*` initialization constants, and descriptor types `union ce_pe_dma_cfg`, `union ce_ring_size`, `union ce_ring_control`, `union ce_io_threshold`, `union ce_part_ring_size`, `struct ce_gd`, `struct ce_sd`, `union ce_pd_ctl`, `union ce_pd_ctl_len`, and `struct ce_pd`.

## Control Flow

There is no executable flow, but core initialization writes these register fields to reset and enable the processing engine, configure rings and byte ordering, seed PRNG, enable interrupts, and push descriptors. Completion flow interprets `ce_pd` control bits such as `PD_CTL_PE_DONE` and `PD_CTL_HOST_READY`.

## State And Persistence Behavior

The header models persistent hardware-visible state: ring base addresses, ring sizes, DMA byte ordering, interrupt state, PRNG seed/result registers, and packet/gather/scatter descriptor ownership bits. Structures are packed because hardware consumes their exact layout.

## Dependencies And Integration Points

It is included by both core and algorithm headers and binds software layout to the PPC4xx Security Subsystem specification. It integrates with DMA coherent memory allocated by the core file.

## Risks And Test Signals

Risks include bitfield layout dependency on compiler/endian behavior, typo-prone register offsets, conflated interrupt clear/mask offsets, and packet length/status field mistakes. Test on big-endian PPC hardware, use hardware register traces, run DMA descriptor selftests, and compare structure sizes/offsets against the datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_reg_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_sa.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_sa.h

## Purpose

`crypto4xx_sa.h` defines dynamic Security Association command words, content masks, state records, and SA layouts for AES, CCM, GCM, and HMAC-SHA1 operations on the PPC4xx crypto engine.

## Important APIs, Types, And Functions

Key definitions are `union dynamic_sa_contents`, `union sa_command_0`, `union sa_command_1`, `struct dynamic_sa_ctl`, `struct sa_state_record`, AES/CCM/GCM/hash SA structs, length/content macros such as `SA_AES128_LEN`, `SA_AES_CONTENTS`, `SA_AES_GCM_CONTENTS`, and accessors `get_dynamic_sa_offset_state_ptr_field()`, `get_dynamic_sa_key_field()`, and `get_dynamic_sa_inner_digest()`.

## Control Flow

The header has no standalone execution. Algorithm setkey code fills these command fields and key/digest locations, while `crypto4xx_build_pd()` computes and writes the state-record pointer into the dynamic SA before descriptor submission.

## State And Persistence Behavior

SA buffers persist per TFM in `crypto4xx_ctx` until rekey or exit. Per-packet shadow SAs and state records persist in DMA-coherent pools until descriptor completion. Saved IV and digest fields carry final IV and AEAD tag material back from hardware.

## Dependencies And Integration Points

It is consumed by `crypto4xx_alg.c` and `crypto4xx_core.c`, and its layouts must match the hardware dynamic SA ABI described by the PPC4xx Security Subsystem. It relies on packed structures and little-endian fields inside otherwise PowerPC-oriented code.

## Risks And Test Signals

Risks include state-pointer offset computation errors, incorrect content masks for variable key sizes, bitfield packing differences, GCM inner digest placement mistakes, and confusion between inbound/outbound direction plus opcode. Test every key size, ECB/CBC/CTR/CCM/GCM vectors, saved IV updates, auth tag generation/checking, and structure offset assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_sa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_trng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_trng.c

## Purpose

`crypto4xx_trng.c` provides optional hwrng support for PPC4xx true random generator blocks associated with the AMCC crypto engine.

## Important APIs, Types, And Functions

The main functions are `ppc4xx_trng_probe()`, `ppc4xx_trng_remove()`, `ppc4xx_trng_data_present()`, `ppc4xx_trng_data_read()`, and `ppc4xx_trng_enable()`. It defines local TRNG control/status/data offsets and matches `ppc4xx-rng`, `amcc,ppc460ex-rng`, and `amcc,ppc440epx-rng`.

## Control Flow

Probe finds an available matching TRNG node, maps resource 0, allocates an `hwrng`, assigns data-present/read callbacks, stores it in `core_dev`, enables TRNG in the crypto engine device-control register, writes the TRNG control mode, and registers with `devm_hwrng_register()`. Data-present polls the busy bit up to 20 times with 10 us delays when waiting. Read returns one 32-bit value from the data register. Remove unregisters, disables the TRNG bit, unmaps MMIO, and frees the hwrng object.

## State And Persistence Behavior

TRNG state is held in `dev->trng_base` and `core_dev->trng`. Hardware enablement persists in `CRYPTO4XX_DEVICE_CTRL` until remove disables it. The hwrng object uses `rng->priv` to point back to the crypto4xx device.

## Dependencies And Integration Points

It integrates with OF node lookup, MMIO mapping, hwrng, endian IO helpers, and the core crypto device's main MMIO register block. It is compiled only when `CONFIG_HW_RANDOM_PPC4XX` is enabled.

## Risks And Test Signals

Risks include manual freeing after devm hwrng registration, missing `dev->trng_base` null checks on partial failures, polling semantics that report present when `wait` is false even if busy, and cross-node assumptions between crypto and RNG blocks. Test hwrng registration/removal, absent or disabled TRNG nodes, repeated reads under rngtest, module unload, and busy-bit timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_trng.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_trng.h

## Purpose

`crypto4xx_trng.h` conditionally exposes TRNG probe/remove hooks to the crypto4xx core while compiling them away when PPC4xx hwrng support is disabled.

## Important APIs, Types, And Functions

It declares `ppc4xx_trng_probe()` and `ppc4xx_trng_remove()` under `CONFIG_HW_RANDOM_PPC4XX`, otherwise provides inline no-op definitions with `__maybe_unused` parameters.

## Control Flow

The header itself has no runtime flow. It lets `crypto4xx_core.c` call the TRNG hooks unconditionally from probe/remove without requiring conditional code in the core file.

## State And Persistence Behavior

No state is stored here. State effects depend on whether the real implementation is linked.

## Dependencies And Integration Points

It depends on `struct crypto4xx_core_device` from `crypto4xx_core.h` and the `HW_RANDOM_PPC4XX` Kconfig symbol. The Makefile conditional object must match this header's conditions.

## Risks And Test Signals

Risks include config mismatch between header and Makefile, missing forward declarations if include order changes, and silent no-op behavior when users expect hwrng. Test builds with `HW_RANDOM_PPC4XX=y/m/n` and probe logs on systems with TRNG nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_trng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/Kconfig

## Purpose

`amlogic/Kconfig` defines the build options for the Amlogic GXL crypto offloader and its debug stats support.

## Important APIs, Types, And Functions

`CRYPTO_DEV_AMLOGIC_GXL` is a tristate depending on `HAS_IOMEM`, defaulting to module on `ARCH_MESON`, selecting `CRYPTO_SKCIPHER`, `CRYPTO_ENGINE`, `CRYPTO_ECB`, `CRYPTO_CBC`, and `CRYPTO_AES`. `CRYPTO_DEV_AMLOGIC_GXL_DEBUG` is a debugfs-dependent bool for stats/debug output.

## Control Flow

There is no runtime flow. Config selection controls whether the driver is built and whether debug counters/debugfs stats are compiled.

## State And Persistence Behavior

No runtime state is held here. Build configuration persists into which symbols, debug counters, and module objects are present.

## Dependencies And Integration Points

It integrates the Amlogic driver into the crypto driver Kconfig hierarchy and ensures required CryptoAPI algorithm helpers are available. The module name documented here matches the Makefile output.

## Risks And Test Signals

Risks include missing dependency on clocks or OF/platform support, debug option enabled in production affecting timing, and default module selection surprises on Meson platforms. Test `allyesconfig`, `allmodconfig`, `ARCH_MESON`, and `COMPILE_TEST`-like builds if dependency policy changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/Makefile

## Purpose

This Makefile builds the Amlogic GXL crypto offloader module from its core and cipher implementation files.

## Important APIs, Types, And Functions

It declares `obj-$(CONFIG_CRYPTO_DEV_AMLOGIC_GXL) += amlogic-gxl-crypto.o` and sets `amlogic-gxl-crypto-y := amlogic-gxl-core.o amlogic-gxl-cipher.o`.

## Control Flow

There is no runtime control flow. Build-time selection links the platform registration and AES cipher code into one module.

## State And Persistence Behavior

No runtime state is stored. The composite object determines which driver code is available.

## Dependencies And Integration Points

It integrates with kbuild and the `CRYPTO_DEV_AMLOGIC_GXL` Kconfig option. It must stay aligned with prototypes in `amlogic-gxl.h` and templates in `amlogic-gxl-core.c`.

## Risks And Test Signals

Risks are limited to object list drift and module-name mismatch. Test module and built-in builds with `CONFIG_CRYPTO_DEV_AMLOGIC_GXL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl-cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl-cipher.c

## Purpose

`amlogic-gxl-cipher.c` implements AES ECB/CBC skcipher acceleration for the Amlogic GXL crypto block, with fallback for zero-length and scatterlist shapes the descriptor engine cannot process.

## Important APIs, Types, And Functions

Key functions are `get_engine_number()`, `meson_cipher_need_fallback()`, `meson_cipher_do_fallback()`, `meson_cipher()`, `meson_handle_cipher_request()`, `meson_skencrypt()`, `meson_skdecrypt()`, `meson_cipher_init()`, `meson_cipher_exit()`, and `meson_aes_setkey()`. The hardware path fills `struct meson_desc` entries in a per-flow coherent descriptor list.

## Control Flow

Encrypt/decrypt set direction, fallback if source/destination SG counts differ, descriptor budget is exceeded, segments are not 16-byte aligned/length, offsets are not word aligned, or lengths differ. Hardware requests select a flow and queue to its crypto engine. `meson_cipher()` creates a DMA buffer containing key and optional IV, emits two key descriptors plus optional IV descriptor, maps SGs, emits data descriptors with mode, blockmode, direction, owner, and last bits, starts the flow by writing descriptor-list physical address to the flow register, waits for IRQ completion, unmaps DMA, and updates the caller IV from the last ciphertext block or saved decrypt IV.

## State And Persistence Behavior

TFM state stores copied key, key length, key mode, device pointer, and fallback TFM. Request state stores direction, selected flow, and fallback request. Per-flow descriptor memory and completion status persist in `meson_dev`. The bus clock remains enabled for the lifetime of the probed device; no runtime PM is implemented.

## Dependencies And Integration Points

It depends on `amlogic-gxl-core.c` for flow allocation, IRQs, algorithm registration, and crypto-engine queues. It uses CryptoAPI skcipher internals, scatterwalk, DMA mapping, and Amlogic descriptor constants from `amlogic-gxl.h`.

## Risks And Test Signals

Risks include descriptor count assumptions for key/IV, IV size vs cryptlen validation, missing DMA unmap on some early mapping failures, no runtime PM, reliance on equal SG layouts, and timeout at 500 ms. Test AES ECB/CBC vectors, in-place and out-of-place requests, multi-SG layouts, fallback counters, IV update behavior, DMA API debugging, and IRQ timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl-cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl-core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl-core.c

## Purpose

`amlogic-gxl-core.c` is the platform driver and CryptoAPI registration layer for the Amlogic GXL crypto offloader. It manages MMIO, clock enablement, flow engines, IRQ completion, algorithm templates, debugfs, and probe/remove.

## Important APIs, Types, And Functions

Important functions are `meson_crypto_probe()`, `meson_crypto_remove()`, `meson_allocate_chanlist()`, `meson_free_chanlist()`, `meson_register_algs()`, `meson_unregister_algs()`, `meson_irq_handler()`, and `meson_debugfs_show()`. `mc_algs[]` registers `cbc(aes)` and `ecb(aes)` as crypto-engine skcipher algorithms.

## Control Flow

Probe allocates `meson_dev`, maps resource 0, gets and enables `blkmv` clock, obtains two IRQs, requests both with a shared handler, allocates two flow engines and coherent descriptor lists, registers algorithms, and creates optional debugfs stats. The IRQ handler identifies the flow by IRQ number, reads the flow status register, clears it, marks completion, and wakes the waiting crypto-engine worker. Remove removes debugfs, unregisters algorithms, frees flow engines/descriptors, and disables the clock.

## State And Persistence Behavior

Persistent state includes MMIO base, bus clock, device pointer, flow list, round-robin atomic, IRQ array, and optional debugfs dentry. Each flow persists a crypto engine, completion, status, descriptor list physical/virtual addresses, and optional request counter. Hardware state is not saved across suspend because no PM hooks are defined.

## Dependencies And Integration Points

It integrates with platform/OF matching for `amlogic,gxl-crypto`, common clock, IRQs, coherent DMA, `crypto_engine`, internal skcipher registration, and debugfs.

## Risks And Test Signals

Risks include no reset/runtime-PM handling, per-flow IRQ/register mapping mistakes, failure unwind ordering, algorithm template global state across multiple devices, and status clearing semantics. Test probe/remove, both flows, IRQ routing, clock gating, debugfs stats, multi-device assumptions, and CryptoAPI selftests on GXL hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl.h

## Purpose

`amlogic-gxl.h` defines the shared descriptor format, mode bits, flow/device/TFM/request state, algorithm template, and prototypes for the Amlogic GXL crypto driver.

## Important APIs, Types, And Functions

Key constants include key modes, encrypt/decrypt values, ECB/CBC modes, `MAXFLOW`, `MAXDESC`, and descriptor status bits `DESC_LAST`, `DESC_ENCRYPTION`, and `DESC_OWN`. Key types are `struct meson_desc`, `struct meson_flow`, `struct meson_dev`, `struct meson_cipher_req_ctx`, `struct meson_cipher_tfm_ctx`, and `struct meson_alg_template`.

## Control Flow

The header has no executable flow. Core code allocates flows and descriptor lists; cipher code fills `meson_desc` entries according to the bit layout documented here and submits them by writing flow registers.

## State And Persistence Behavior

Persistent state defined here includes per-device MMIO/clock/flow/IRQ/debug state, per-flow coherent descriptor memory and completion state, per-request direction/flow/fallback storage, and per-TFM key/fallback state.

## Dependencies And Integration Points

It integrates CryptoAPI AES/skcipher/engine headers, debugfs, scatterlists, and driver-internal prototypes. The descriptor layout is based on reverse-engineered or undocumented fields noted in comments, making it the local hardware ABI reference.

## Risks And Test Signals

Risks include undocumented descriptor bits, fixed descriptor count, no include guard, fallback request placement, and key pointer typed as `u32 *` while allocated from byte keys. Test build warnings, descriptor dumps against hardware behavior, all AES key sizes, and request-size calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/Kconfig

## Purpose

`aspeed/Kconfig` defines the configuration surface for Aspeed crypto support, including the base HACE/crypto engine driver, optional debug messages, HACE hash support, HACE symmetric crypto support, and ACRY RSA support.

## Important APIs, Types, And Functions

The main symbol is `CRYPTO_DEV_ASPEED`, a tristate depending on `ARCH_ASPEED || COMPILE_TEST` and selecting `CRYPTO_ENGINE`. Optional symbols are `CRYPTO_DEV_ASPEED_DEBUG`, `CRYPTO_DEV_ASPEED_HACE_HASH`, `CRYPTO_DEV_ASPEED_HACE_CRYPTO`, and `CRYPTO_DEV_ASPEED_ACRY`, which select SHA/HMAC, AES/DES/ECB/CBC/CTR, or RSA dependencies as needed.

## Control Flow

There is no runtime flow. Config choices determine whether the shared Aspeed crypto module is built and which HACE hash, HACE cipher, and ACRY RSA implementation objects are linked.

## State And Persistence Behavior

No runtime state is stored here. Build-time state controls available algorithms and whether extra debug messages are compiled.

## Dependencies And Integration Points

It integrates Aspeed crypto drivers into the kernel crypto Kconfig tree and supplies dependency selection for downstream Makefile object composition. The help text documents HACE digest/cipher capabilities and ACRY RSA range.

## Risks And Test Signals

Risks include optional feature combinations that leave the base driver without any algorithms, debug messages affecting timing, and dependency omissions when algorithm coverage changes. Test all Aspeed config combinations, `COMPILE_TEST`, module/built-in builds, and Kconfig dependency resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/Makefile

## Purpose

This Makefile composes the Aspeed crypto driver objects based on selected HACE hash, HACE symmetric crypto, and ACRY RSA Kconfig features.

## Important APIs, Types, And Functions

It conditionally maps `hace-hash-y` to `aspeed-hace-hash.o`, `hace-crypto-y` to `aspeed-hace-crypto.o`, builds `aspeed_crypto.o` from `aspeed-hace.o` plus selected HACE objects, conditionally maps `aspeed_acry-y` to `aspeed-acry.o`, and adds both composite/base objects under `obj-$(CONFIG_CRYPTO_DEV_ASPEED)`.

## Control Flow

There is no runtime control flow. The Makefile determines whether the shared HACE platform object is linked with hash, cipher, both, or neither, and whether RSA ACRY support is also built.

## State And Persistence Behavior

No runtime state is stored here. The build artifact composition persists as available driver code in the kernel or module.

## Dependencies And Integration Points

It integrates with `CRYPTO_DEV_ASPEED`, `CRYPTO_DEV_ASPEED_HACE_HASH`, `CRYPTO_DEV_ASPEED_HACE_CRYPTO`, and `CRYPTO_DEV_ASPEED_ACRY` symbols. It must remain consistent with object filenames and Kconfig feature dependencies.

## Risks And Test Signals

Risks include building `aspeed_crypto.o` without feature objects when both HACE options are off, adding `aspeed-acry.o` under the base symbol rather than a separate object target, and object-name drift. Test all feature combinations and verify expected algorithms register for hash, cipher, and RSA configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/Makefile -->
