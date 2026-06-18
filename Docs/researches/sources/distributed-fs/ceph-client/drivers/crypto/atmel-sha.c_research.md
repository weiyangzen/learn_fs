# sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha.c

## Purpose

`atmel-sha.c` is the Atmel/Microchip SHA hardware acceleration driver. It registers asynchronous kernel-only ahash algorithms for SHA1/SHA256 universally, SHA224/SHA384/SHA512 and HMAC variants when the hardware version supports them, and exports an internal authenc service used by `atmel-aes.c`. It handles streaming hash state, CPU, DMA, and legacy PDC transfers, HMAC precomputation, request queuing, and hardware capability detection.

## Important APIs, Types, And Functions

Core state types are `struct atmel_sha_dev`, `struct atmel_sha_reqctx`, `struct atmel_sha_ctx`, `struct atmel_sha_hmac_ctx`, `struct atmel_sha_dma`, and optional `struct atmel_sha_authenc_ctx`. Main callbacks are `atmel_sha_init/update/final/finup/digest/export/import()`. `atmel_sha_handle_queue()`, `atmel_sha_start()`, and `atmel_sha_done()` run the async state machine. Transfer helpers include `atmel_sha_update_dma_start()`, `atmel_sha_xmit_dma()`, `atmel_sha_xmit_pdc()`, and `atmel_sha_cpu_start()`. HMAC uses `atmel_sha_hmac_setup()` and related prehash/ipad/opad functions. Authenc exports readiness, spawn/free, setkey, schedule, init, final, and abort helpers.

## Control Flow

Probe maps registers, requests a shared IRQ, prepares the SHA clock, reads hardware version, derives capabilities, requests a TX DMA channel when available, adds the device to the global list, and registers algorithms. Hash init selects algorithm flags and block size. Updates either buffer short data, use CPU for short finup, or map suitable scatterlist data for DMA/PDC. Final appends SHA padding and drives the last block. Interrupts mark output/DMA readiness and schedule a tasklet, which unmaps DMA, loops over remaining data, copies digest registers, finalizes requests, disables the clock, and starts the next queue item. HMAC precomputes ipad/opad hashes and uses UIHV when available; authenc lets AES temporarily drive SHA in IDATAR0/HMAC/dual-buffer mode.

## State And Persistence Behavior

Request state preserves digest bytes, 128-bit byte counters, buffered data, SG walk position, block/hash sizes, DMA address, operation, and flags for final/pad/restore/error. Transform state stores the device and start callback; HMAC transform state additionally caches pending keys and precomputed ipad/opad hash values. Device state stores queue, current request, DMA channel, tasklets, flags, resume callbacks, and capabilities. Hardware digest context can persist across updates; when UIHV is available the driver saves/restores digest registers for concurrent request interleaving.

## Dependencies And Integration Points

The driver depends on ahash crypto APIs, DMAengine, scatterwalk, platform/OF, clocks, IRQ/tasklets, `atmel-sha-regs.h`, and optionally `atmel-authenc.h`. It is the SHA-side provider for AES authenc and must be probed before AES registers authenc-capable algorithms.

## Risks And Test Signals

Risks include subtle padding/count bugs, DMA/PDC unmap errors, SG length mutation in alignment checks, concurrent streaming requests on hardware without UIHV, HMAC key prehash lifetime, authenc callback/abort ordering, empty-message HMAC special cases, and registration unwind mistakes when capabilities vary. Test SHA and HMAC crypto selftests for all advertised digests, streaming/export/import, short CPU path versus DMA/PDC threshold, unaligned and zero-length SGs, interleaved requests, AES authenc integration, driver unbind, DMA fault injection, and real hardware versions from 0x320 through 0x800.
