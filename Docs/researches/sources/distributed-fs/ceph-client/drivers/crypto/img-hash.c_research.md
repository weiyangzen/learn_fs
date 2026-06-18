# sources/distributed-fs/ceph-client/drivers/crypto/img-hash.c

## Purpose
This file implements the Imagination Technologies MD5/SHA1/SHA224/SHA256 hash accelerator as a platform driver and asynchronous hash provider. Digest requests can be processed by the hardware directly while update/final/import/export flows use software fallback transforms.

## Important APIs, Types, And Functions
Core types are `struct img_hash_dev` for one hardware device, `struct img_hash_ctx` for per-transform state and fallback ahash, `struct img_hash_request_ctx` for per-request digest/DMA/scatterlist state, and global `struct img_hash_drv img_hash` for the device list. Algorithms are registered in `img_algs[]`.

Important functions include `img_hash_probe()` and `img_hash_remove()` for platform lifecycle, `img_register_algs()` and `img_unregister_algs()`, `img_hash_digest()` for hardware digest submission, `img_hash_handle_queue()` for serialized request queueing, `img_hash_hw_init()` and `img_hash_start()` for register programming, `img_hash_write_via_cpu()` and `img_hash_write_via_dma()` for data transfer, `img_hash_dma_task()` and `img_hash_done_task()` tasklets, and `img_irq_handler()` for completion interrupts. Fallback setup is in `img_hash_cra_init()` with `md5-lib`, `sha1-lib`, `sha224-lib`, or `sha256-lib`.

## Control Flow
Probe maps two MMIO resources, requests an IRQ, enables `hash` and `sys` clocks, configures a DMA channel, adds the device to the global list, and registers four ahash algorithms. A digest request selects a device, sets digest flags by digest size, initializes scatterlist walk state, and enqueues on the per-device crypto queue. The queue handler initializes hardware message length and algorithm mode, then chooses DMA for requests at least 64 bytes or CPU writes for smaller requests.

DMA transfer walks one scatterlist segment at a time and rounds each DMA transfer down to a 4-byte multiple because hardware lacks a data-valid mask. Leftover bytes are buffered and prepended to the next transfer or sent by CPU. Interrupts set output-ready and DMA-ready flags and schedule the done tasklet, which unmaps DMA, reads result words in reverse order from the result queue, copies the digest to the caller, completes the request, and advances the queue.

## State And Persistence
Runtime state includes the global device list, per-device spinlock, queue, active request pointer, tasklets, DMA channel, clocks, MMIO bases, and flags. Per-request state tracks digest bytes, sg cursor, offset, bytes sent, temporary buffer, and fallback request. No persistent state exists; hardware is reset per request.

## Dependencies And Integration Points
The driver depends on platform device resources, device tree compatible `img,hash-accelerator`, clk framework, DMAengine, IRQs, scatterlist helpers, and Crypto API ahash internals. It integrates with software hash libraries through fallback transforms.

## Risks
Only `digest` uses hardware; multi-call update/final paths are fallback-only, so performance differs by API usage. Queue handling serializes one request per device. DMA error fallback to CPU is partial and relies on correctly resetting `hdev->err`. `img_hash_write_via_cpu()` appears to set `ctx->bufcnt` from `sg_copy_to_buffer()` and then zero it before transmitting `ctx->buffer`, which is suspicious because the copied byte count is discarded while `ctx->total` is retained. Suspend disables clocks without explicit queue quiescing in this file.

## Test Signals
Run ahash known-answer tests for md5, sha1, sha224, and sha256 using digest, update/final, finup, import/export. Exercise small CPU path, DMA path, unaligned scatterlists, multi-SG leftovers, zero-length digest, DMA channel failure, IRQ error bits, suspend/resume, and concurrent requests to validate queue/backlog behavior.
