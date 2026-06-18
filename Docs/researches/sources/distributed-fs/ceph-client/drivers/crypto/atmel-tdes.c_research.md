# sources/distributed-fs/ceph-client/drivers/crypto/atmel-tdes.c

## Purpose

This file implements the Atmel DES/TDES hardware accelerator as a Linux kernel asynchronous `skcipher` provider. It exposes ECB and CBC variants for DES and 3DES-EDE through the kernel crypto API, programs the TDES mode/key/IV registers, and moves request data through either the peripheral DMA controller style register interface or DMAengine channels depending on the detected hardware version.

## Important APIs, Types, and Functions

- `struct atmel_tdes_dev` is the per-device runtime state: MMIO base, physical base, clock, IRQ, crypto queue, tasklets, current request, scatterlist cursors, bounce pages, DMA addresses, DMA channels, capability flags, and hardware version.
- `struct atmel_tdes_ctx` is the per-transform crypto context: selected hardware device, key material, key length, mode flags, and block size.
- `struct atmel_tdes_reqctx` stores per-request mode bits and the last ciphertext block needed to update CBC IV on decrypt completion.
- `atmel_tdes_probe()` maps registers, requests IRQ and clock, reads version, determines DMA capability, allocates bounce buffers, optionally requests DMA channels, adds the device to the global list, and registers algorithms.
- `atmel_tdes_handle_queue()` serializes async requests through `struct crypto_queue`, marks the hardware busy, configures registers, and starts the first transfer chunk.
- `atmel_tdes_crypt_start()` selects a fast direct scatterlist DMA path when source and destination are aligned and size-compatible, otherwise copies through pre-mapped page-sized bounce buffers.
- `atmel_tdes_crypt_pdc()` programs TDES transmit/receive pointer and count registers and enables end-of-receive interrupts for non-DMAengine devices.
- `atmel_tdes_crypt_dma()` configures two DMAengine slave channels, builds one-entry DMA scatterlists for input and output, and schedules completion from the output channel callback.
- `atmel_tdes_done_task()` stops the current transfer, copies bounce data back when needed, starts the next chunk, or completes the request and advances the queue.
- `atmel_des_setkey()` and `atmel_tdes_setkey()` use kernel DES/3DES key validators before storing key bytes.

## Control Flow

Crypto API encrypt/decrypt callbacks call `atmel_tdes_crypt()` with mode flags. The request is rejected if its length is zero or not a multiple of `DES_BLOCK_SIZE`; CBC decrypt saves the last input ciphertext block before hardware mutates the destination. The request is enqueued, and if the device is idle, `atmel_tdes_handle_queue()` dequeues one request, installs it as `dd->req`, copies mode flags into `dd->flags`, writes the mode/key/IV registers through `atmel_tdes_write_ctrl()`, then starts transfer.

Transfer execution is chunked. The fast path maps one input and one output scatterlist entry directly. The fallback path copies from source scatterlists into `buf_in`, submits a page-sized or smaller DMA/PDC transaction, then copies from `buf_out` back to destination scatterlists during stop handling. PDC completion is IRQ driven through `atmel_tdes_irq()`, while DMAengine completion schedules the same done task through `atmel_tdes_dma_callback()`.

Completion updates CBC IV to match crypto API semantics: encryption copies the last destination ciphertext block to `req->iv`, and decryption restores the last source ciphertext block saved before the request. The clock is disabled, `TDES_FLAGS_BUSY` is cleared, the request callback is invoked, and queued work is resumed.

## State and Persistence Behavior

The driver has no persistent on-disk state. Runtime state is held in the global `atmel_tdes.dev_list`, the per-device queue, DMA mappings, bounce pages, tasklets, and per-transform contexts. Key material persists only in the lifetime of `struct atmel_tdes_ctx`; bounce buffers are allocated at probe and reused for requests. `TDES_FLAGS_INIT` records that a hardware reset has already been issued after the clock was enabled. Hardware capabilities are derived from the major bits of `TDES_HW_VERSION` and cached in `dd->caps.has_dma`.

## Dependencies and Integration Points

The file depends on the kernel crypto `skcipher` API, DMA mapping APIs, DMAengine, platform device resources, device tree matching for `atmel,at91sam9g46-tdes`, an input clock named `tdes_clk`, IRQ delivery, and register definitions from `atmel-tdes-regs.h`. It registers four kernel crypto algorithms: `ecb(des)`, `cbc(des)`, `ecb(des3_ede)`, and `cbc(des3_ede)`, with driver-only async flags and priority 300. It integrates with platform probe/remove lifecycle and with Atmel DMA channel names `tx` and `rx` when hardware supports DMAengine.

## Risks and Edge Cases

- The driver serializes all requests through one hardware device; queue starvation or stuck interrupts would block later requests.
- Fast path eligibility relies on alignment, scatterlist DMA lengths, and equal input/output DMA lengths. Misclassification would risk DMA mapping or short-copy errors.
- Bounce-copy code must maintain `in_sg`, `out_sg`, and offsets exactly across chunks; errors are reported if copied byte counts do not match `dma_size`.
- Request lengths must be DES-block aligned; callers that expect streaming or CTS-like behavior will receive `-EINVAL`.
- CBC IV update semantics are subtle for decrypt because the last ciphertext block must be captured before destination overwrite.
- DMAengine submission has separate input and output descriptors; if output submission succeeds and input setup later fails, cleanup paths need to avoid leaks and stale flags.
- Probe error unwind must kill tasklets and free DMA/bounce resources in the correct order.

## Test Signals

Useful signals include successful registration in `/proc/crypto` for the four Atmel driver names, `tcrypt` or crypto manager self-tests for DES/3DES ECB/CBC encrypt and decrypt, CBC IV mutation tests across multi-block requests, scatterlist tests with unaligned offsets to force bounce buffering, large requests spanning multiple chunks, both DMA-capable and PDC-only hardware versions, DMA channel absence during probe, shared IRQ spurious interrupt handling, and module remove after active algorithm registration.
