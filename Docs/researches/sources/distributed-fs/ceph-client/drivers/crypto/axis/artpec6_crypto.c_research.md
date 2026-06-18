# sources/distributed-fs/ceph-client/drivers/crypto/axis/artpec6_crypto.c

## Purpose

This file implements the Axis ARTPEC-6 and ARTPEC-7 cryptographic accelerator driver. It registers asynchronous SHA-1, SHA-256, HMAC-SHA256, AES ECB/CBC/CTR/XTS skciphers, and AES-GCM AEAD algorithms. The hardware is driven through a coupled packet DMA engine whose descriptors carry short metadata packets, key packets, source data, destination buffers, and status descriptors.

## Important APIs, Types, and Functions

- `struct artpec6_crypto` is the device state: MMIO base, queue lock, waiting queue, pending list, tasklet, descriptor slab cache, pending count, timeout timer, hardware variant, and cache-aligned padding buffers.
- `struct artpec6_crypto_dma_descriptors` holds the 64-entry OUT descriptor array, IN descriptor array, status array, DMA mappings, and bounce-buffer list for one request.
- `struct artpec6_crypto_req_common` embeds common request state for skcipher, ahash, and AEAD paths, including the parent `crypto_async_request` and completion callback.
- `struct artpec6_cryptotfm_context`, `struct artpec6_crypto_request_context`, `struct artpec6_hash_request_context`, and `struct artpec6_crypto_aead_req_ctx` store transform and request-specific key, metadata, hash partials, digest state, IV/GCM context, and decrypt tag buffers.
- Descriptor helpers such as `artpec6_crypto_setup_out_descr*()`, `artpec6_crypto_setup_in_descr*()`, `artpec6_crypto_setup_sg_descrs_out()`, and `artpec6_crypto_setup_sg_descrs_in()` build hardware packets from virtual buffers and scatterlists.
- `artpec6_crypto_prepare_crypto()`, `artpec6_crypto_prepare_hash()`, and `artpec6_crypto_prepare_aead()` convert crypto API requests into PDMA descriptor chains.
- `artpec6_crypto_submit()`, `artpec6_crypto_start_dma()`, `artpec6_crypto_irq()`, `artpec6_crypto_task()`, and `artpec6_crypto_process_queue()` implement scheduling, hardware submission, interrupt acknowledgement, status polling, and completion.
- `init_crypto_hw()` and `artpec6_crypto_disable_hw()` configure or stop ARTPEC-6 versus ARTPEC-7 PDMA registers.

## Control Flow

For skcipher requests, encrypt/decrypt callbacks set the decrypt flag, allocate a descriptor object from the slab cache, prepare key-download descriptors, cipher metadata, IV descriptors, source OUT descriptors, destination IN descriptors, and CTR/XTS padding when needed. CTR requests first check whether the hardware's 32-bit counter field would overflow; if so they fall back to a synchronous software skcipher allocated during CTR transform init.

For hash requests, init sets metadata for SHA-1, SHA-256, or HMAC-SHA256. Update and final operations manage `partial_buffer`, `digeststate`, and `digcnt`. Non-final updates only send full hash blocks to hardware and retain trailing bytes. Final operations append software-created hash padding and route the final digest into `areq->result`. HMAC uploads the key as the first packet and uses a child shash only to shorten overlong HMAC keys.

For AEAD, the driver supports AES-GCM. Preparation downloads the AES key, sends cipher metadata, constructs a hardware context containing AAD length, text length, and J0, streams AAD and plaintext/ciphertext with mandatory zero padding, and routes output data and tags. Decrypt stores the hardware tag in a request-local buffer and compares it against the input tag during completion, returning `-EBADMSG` on mismatch.

Submission is global because `artpec6_crypto_dev` points to the single registered device. If the PDMA pending count is not above the driver's busy threshold, a request moves directly to `pending` and descriptors are pushed to IN, STAT, and OUT queues. Otherwise MAY_BACKLOG requests are queued, and non-backlog requests are destroyed with `-EBUSY`. The IRQ acknowledges data and EOP-flush interrupts, flushes status when needed, and schedules a tasklet only when status should be readable. The tasklet scans pending requests until it finds a zero final status, unmaps DMA, copies bounce buffers back, destroys request resources, invokes completion callbacks outside the spinlock, and starts queued work. A timer reschedules the tasklet if hardware raises an interrupt before the status descriptor becomes visible.

## State and Persistence Behavior

No state persists beyond runtime. Per-request descriptor arrays and DMA mappings are allocated from `ac->dma_cache` and freed at completion or submission failure. Bounce buffers are allocated only for destination fragments that are not cache-line safe and copied back before freeing. Hash export/import persists only crypto API incremental hash state: partial block, digest state, byte count, and operation metadata. The global `artpec6_crypto_dev` enforces a single active hardware instance.

## Dependencies and Integration Points

The driver depends on platform device probing, OF compatibles `axis,artpec6-crypto` and `axis,artpec7-crypto`, MMIO resources, one IRQ, DMA mapping APIs, the kernel crypto ahash/skcipher/AEAD internals, scatterwalk helpers, AES/GCM/SHA constants, XTS key verification, debugfs, and optional fault injection. It registers algorithms through `crypto_register_ahashes()`, `crypto_register_skciphers()`, and `crypto_register_aeads()`. The Makefile builds it under `CONFIG_CRYPTO_DEV_ARTPEC6`.

## Risks and Edge Cases

- Descriptor arrays are capped at 64 entries. Fragmented scatterlists, metadata packets, padding, and bounce buffers can exhaust descriptors and return `-ENOSPC`.
- The driver uses physical addresses from scatterlists and manual DMA mapping, so cache-line ownership rules are critical; destination fragments smaller than or unaligned to `ARTPEC_CACHE_LINE_MAX` must use bounce buffers.
- The global device pointer prevents multiple devices and makes all crypto transforms depend on probe ordering and clean remove.
- Status visibility is known to race with interrupts; the timeout path is a mitigation that should be tested under stress.
- AES-GCM decrypt writes plaintext before tag comparison. Consumers must respect the AEAD API rule that plaintext is invalid on `-EBADMSG`.
- CTR fallback covers whole-IV counter overflow because hardware increments only the low 32 bits.
- Hash partial and export/import state must stay consistent across update/final sequences, especially HMAC key upload and no-start update paths.
- Remove must unregister algorithms before disabling hardware and destroying the descriptor cache to avoid use-after-free from new requests.

## Test Signals

High-value tests include crypto manager self-tests for all registered algorithms, AES-CTR vectors that overflow the low 32-bit counter and require fallback, fragmented and unaligned scatterlists to exercise short descriptors and bounce buffers, descriptor exhaustion through fault injection or heavily split SG lists, GCM tag mismatch returning `-EBADMSG`, incremental hash export/import round trips, HMAC keys longer than the block size, concurrent async requests to exercise pending/backlog transitions, ARTPEC-6 and ARTPEC-7 register offset variants, debugfs fault injection for status-read timeout, and module remove after queued work drains.
