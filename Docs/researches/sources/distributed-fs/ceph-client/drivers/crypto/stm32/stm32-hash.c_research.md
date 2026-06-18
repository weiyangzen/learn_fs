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
