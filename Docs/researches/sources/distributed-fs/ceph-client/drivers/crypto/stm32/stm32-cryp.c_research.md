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
