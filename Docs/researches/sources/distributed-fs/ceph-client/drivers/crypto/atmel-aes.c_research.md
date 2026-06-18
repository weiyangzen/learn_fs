# sources/distributed-fs/ceph-client/drivers/crypto/atmel-aes.c

## Purpose

`atmel-aes.c` is the Atmel/Microchip AES hardware acceleration driver. It registers asynchronous kernel-only skcipher algorithms for AES ECB/CBC/CTR, optionally GCM AEAD, XTS, and authenc(HMAC-SHA*,CBC-AES) depending on hardware version and SHA-driver availability. It multiplexes one hardware AES device through a crypto queue, uses CPU register writes for small transfers, DMA for larger aligned transfers, and a bounce buffer for unaligned scatterlists.

## Important APIs, Types, And Functions

Key state types are `struct atmel_aes_dev`, `struct atmel_aes_base_ctx`, mode-specific contexts (`ctr`, `gcm`, `xts`, `authenc`), `struct atmel_aes_reqctx`, and `struct atmel_aes_dma`. `atmel_aes_handle_queue()` serializes requests. `atmel_aes_start()`, `atmel_aes_ctr_start()`, `atmel_aes_gcm_start()`, `atmel_aes_xts_start()`, and `atmel_aes_authenc_start()` implement mode-specific engines. DMA helpers are `atmel_aes_map()`, `atmel_aes_dma_start()`, and `atmel_aes_unmap()`. Registration is controlled by `atmel_aes_get_cap()` and `atmel_aes_register_algs()`.

## Control Flow

Probe maps registers, requests a shared IRQ, prepares `aes_clk`, reads hardware version, derives capabilities, verifies authenc SHA readiness if needed, allocates a 16 KiB bounce buffer, obtains TX/RX DMA channels, adds the device to the global list, and registers algorithms. A crypto request stores mode flags in its request context and enters the device queue. The active request enables the clock, resets/configures the AES block, writes mode/key/IV, and transfers data by CPU or DMA. Interrupts/tasklets resume data-ready or tag-ready state machines; DMA completion unmaps SGs and calls the mode resume function. Completion disables the clock, updates IV for non-ECB skcipher modes, completes async requests, and schedules the next queue item.

## State And Persistence Behavior

Per-transform state stores keys, start callback, block size, AEAD flag, fallback tfm for XTS, and authenc SHA context where enabled. Per-request state stores mode flags, last ciphertext for CBC decrypt IV update, text length/digest for authenc, or GCM/CTR scratch state in the tfm context. Device state stores current async request, active context, busy flags, queue, tasklets, DMA channels, bounce buffer, SG truncation/remainder metadata, and hardware capabilities. Hardware registers are reset at request start and clock-gated at completion.

## Dependencies And Integration Points

The driver depends on the crypto skcipher/AEAD APIs, DMAengine, scatterwalk, common clock, platform/OF, IRQ/tasklets, `atmel-aes-regs.h`, and optionally `atmel-authenc.h`/`atmel-sha.c` for SPLIP authenc. It registers only after the platform device is present and, for authenc-capable hardware, after the SHA authenc service is ready.

## Risks And Test Signals

Risks include queue/device removal races, SG length mutation/restoration bugs, DMA threshold and bounce-buffer overflow mistakes, CTR fragmentation around the 16-bit hardware counter, GCM empty-message/tag quirks, XTS byte-reversed tweak handling, authenc ownership/abort ordering with the SHA driver, and partial algorithm registration unwind. Test with crypto selftests for all registered modes, in-place/out-of-place and unaligned SGs, small CPU path versus large DMA path, CTR counter overflow, GCM non-96-bit IV and empty AAD/text, XTS ciphertext stealing fallback, authenc encrypt/decrypt/tag failure, suspend/unbind, and DMA fault injection.
