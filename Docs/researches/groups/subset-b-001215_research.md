# Research: subset-b-001215

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-tdes.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-tdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/axis/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/axis/Makefile

## Purpose

This Kbuild file connects the Axis ARTPEC crypto driver to the kernel build. It builds `artpec6_crypto.o` when `CONFIG_CRYPTO_DEV_ARTPEC6` is enabled.

## Important APIs, Types, and Functions

There are no C APIs or runtime types in this file. Its only build rule is `obj-$(CONFIG_CRYPTO_DEV_ARTPEC6) := artpec6_crypto.o`, which tells Kbuild to compile and link the ARTPEC-6/ARTPEC-7 crypto platform driver into the crypto driver subtree according to the selected kernel configuration.

## Control Flow

Build-time control flow is entirely configuration driven. If `CONFIG_CRYPTO_DEV_ARTPEC6=y`, the object is linked into the built-in kernel image. If it is `m`, it is built as a module. If unset, the ARTPEC driver is omitted.

## State and Persistence Behavior

The Makefile has no runtime state. The persistent effect is the build artifact selected by Kconfig and the resulting availability of the `artpec6-crypto` platform driver.

## Dependencies and Integration Points

The rule depends on the corresponding Kconfig symbol and on `artpec6_crypto.c`. It integrates with the kernel crypto drivers directory so the platform driver can register ahash, skcipher, and AEAD algorithms when a matching Axis device tree node is present.

## Risks and Edge Cases

- If Kconfig dependencies for `CONFIG_CRYPTO_DEV_ARTPEC6` do not include required crypto API, DMA, platform, or OF support, compile or link failures would surface from `artpec6_crypto.c`.
- Because only one object is listed, any future split of the driver into helper files must update this Makefile or the build will silently miss code.

## Test Signals

Build tests should confirm that `CONFIG_CRYPTO_DEV_ARTPEC6=y` and `m` both produce `artpec6_crypto.o`, and that disabling the symbol omits it. Runtime smoke testing is covered by the ARTPEC driver research section.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/axis/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/axis/artpec6_crypto.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/axis/artpec6_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/Makefile

## Purpose

This Kbuild file defines the Broadcom SPU crypto accelerator build. It produces `bcm_crypto_spu.o` when `CONFIG_CRYPTO_DEV_BCM_SPU` is enabled and links the implementation from `util.o`, `spu.o`, `spu2.o`, and `cipher.o`.

## Important APIs, Types, and Functions

The file has no runtime APIs. The central build rule is `obj-$(CONFIG_CRYPTO_DEV_BCM_SPU) := bcm_crypto_spu.o`, and `bcm_crypto_spu-objs := util.o spu.o spu2.o cipher.o` defines the multi-object module composition. Commented `CFLAGS_* := -DDEBUG` lines document optional per-object debug tracing knobs for developers.

## Control Flow

Build-time control is Kconfig driven. With `CONFIG_CRYPTO_DEV_BCM_SPU=y`, the combined object is built into the kernel. With `m`, it becomes a loadable module. Otherwise none of the SPU implementation objects are included.

## State and Persistence Behavior

There is no runtime state. Persistent impact is the selected build artifact and any developer-local Makefile edits to uncomment debug flags.

## Dependencies and Integration Points

The object list ties `cipher.c` to shared helper and hardware generation code in `util.c`, `spu.c`, and `spu2.c`. `cipher.c` relies on symbols and enums from `spu.h`, `spum.h`, and `spu2.h`, so all listed objects are required for a complete driver.

## Risks and Edge Cases

- Enabling debug CFLAGS can expose sensitive crypto material in logs because `cipher.c` contains packet/key dump paths guarded by debug logging.
- Adding a new hardware-specific helper file without updating `bcm_crypto_spu-objs` will produce unresolved symbols or missing functionality.
- Kconfig dependency mistakes would surface as compile failures across mailbox, crypto API, debugfs, or OF/platform symbols.

## Test Signals

Build with `CONFIG_CRYPTO_DEV_BCM_SPU=y`, `m`, and unset. Confirm the module links all four component objects, and run a debug build only in controlled environments because packet dumps may contain plaintext, keys, IVs, and tags.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/cipher.c

## Purpose

This file is the main Broadcom iProc SPU symmetric crypto offload driver. It registers many kernel crypto API algorithms for skcipher, ahash/HMAC, and AEAD, converts requests into SPU mailbox messages, handles SPU-M and SPU2 generation differences through a function-pointer table, processes asynchronous mailbox responses, and maintains debug/statistics counters.

## Important APIs, Types, and Functions

- `struct bcm_device_private iproc_priv` is the global device object shared with `cipher.h`; it stores platform data, selected SPU hardware callbacks, mailbox channels, counters, debugfs handles, and request statistics.
- `struct iproc_ctx_s` is the per-transform context declared in `cipher.h`: encryption/auth keys, salts, IV storage, algorithm descriptors, max payload, fallback AEAD cipher, HMAC pads, shash fallback state, and SPU header templates.
- `struct iproc_reqctx_s` is the per-request context: crypto parent request, selected mailbox channel, total/sent/received counters, SG cursors, AEAD assoc pointer, IV/counter buffer, hash carry, incremental digest, mailbox message, and embedded fallback AEAD request.
- `spu_functions_register()` populates `struct spu_hw` callbacks for SPU-M or SPU2 implementations.
- `handle_skcipher_req()`, `handle_ahash_req()`, and `handle_aead_req()` build one SPU request chunk, allocate transmit/receive scatterlists, generate SPU headers and padding, and send the mailbox message.
- `spu_rx_callback()` is the asynchronous mailbox receive callback. It validates status, dispatches to response handlers, submits the next chunk if needed, or completes the crypto API request.
- `skcipher_setkey()`, `ahash_hmac_setkey()`, `aead_authenc_setkey()`, `aead_gcm_ccm_setkey()`, and ESP-specific setkey helpers validate and store key material and configure fallback ciphers.
- `spu_register_skcipher()`, `spu_register_ahash()`, `spu_register_aead()`, and `spu_algs_register()` publish the large `driver_algs[]` table to the kernel crypto API.
- `bcm_spu_probe()` reads device tree resources, initializes mailboxes, chooses SPU callbacks, initializes counters/debugfs, and registers algorithms.

## Control Flow

Probe starts by reading the compatible match to select SPU-M NS2, SPU-M NSP, SPU2 v1, or SPU2 v2, maps up to `MAX_SPUS` register resources, counts mailbox channels from the `mboxes` property, requests each mailbox channel, chooses whether SPU messages need an 8-byte BCM header, registers hardware callback functions, initializes statistics, and registers algorithms. Remove unregisters only algorithms marked as registered, frees debugfs, and releases mailboxes.

For skcipher operations, `skcipher_enqueue()` initializes request counters and SG cursors, copies IV/counter material for IV modes, selects a mailbox channel in round-robin order, and calls `handle_skcipher_req()`. That function limits each chunk to `ctx->max_payload`, handles CBC chaining and CTR counter advancement across chunks, finishes a SPU request header from the setkey-time template, builds RX and TX mailbox scatterlists, adds status/padding buffers, and submits via `mailbox_send_message()`.

For ahash, init prepares request counters and either uses hardware incremental hashing or allocates a software `shash` fallback when the hardware cannot support incremental operation. `handle_ahash_req()` carries non-final partial blocks in `hash_carry`, prefixes carried bytes to the next request, chooses hash type/update/final metadata, adds hash padding on the final chunk, and saves incremental digest output for the next hardware request. HMAC on SPU-M performs ipad/opad and outer hash in software; SPU2 can use hardware HMAC for digest-style requests.

For AEAD, `aead_enqueue()` validates associated data size, computes source/destination offsets after AAD, prepares salt+IV for ESP variants, checks hardware fallback requirements, and submits one hardware message. `handle_aead_req()` builds auth/cipher parameters, handles GCM/CCM/ESP/RFC4543 padding and ICV placement, copies input ICV for decrypt modes that include it in the request, and catches output ICV in a separate digest buffer. `handle_aead_resp()` copies generated ICV back to destination for encryption and updates AEAD counters. Hardware status processing maps invalid ICV to `-EBADMSG`.

All operation types complete through `spu_rx_callback()`. The callback processes hardware status, updates per-type response state, continues chunked requests when `total_sent < total_todo`, and finally calls `finish_req()` to free per-chunk mailbox scatterlists and invoke the crypto completion callback.

## State and Persistence Behavior

The driver has global runtime state in `iproc_priv` and per-session state in crypto transform contexts. Request progress is held in `iproc_reqctx_s` across async mailbox callbacks. Incremental hash state can be exported/imported through `struct spu_hash_export_s`, which captures total counters, carry bytes, incremental digest, and software-HMAC flag but deliberately omits transient message buffers. Debug/stat counters persist for the module lifetime and are exposed via debugfs helpers from the companion utility code. Key material persists in transform contexts until tfm exit; fallback AEAD and shash objects are allocated per transform or incremental hash session and freed on exit/final.

## Dependencies and Integration Points

The file depends on the kernel crypto API, authenc key extraction, DES/AES key validation, mailbox framework with Broadcom SPU messages, platform device and OF matching, scatterlist helpers from `util.c`, SPU-M and SPU2 message builders/parsers, debugfs setup/free helpers, random IV generation, and atomic counters. It registers crypto algorithms from `driver_algs[]`, including AES/DES/3DES CBC/ECB, AES CTR/XTS, MD5/SHA/SHA3 hashes and HMACs, AES XCBC/CMAC, AES GCM/CCM, ESP AEAD variants, and many authenc combinations. Some registrations are conditional on hardware generation, such as SHA3 only on SPU2 v2 and limited AES hash modes on SPU-M.

## Risks and Edge Cases

- `iproc_priv` is a single global, so multiple platform devices would share mutable state and are not naturally isolated.
- Debug logging can dump keys, IVs, plaintext, ciphertext, AAD, and tags; module parameters must be treated as sensitive.
- Chunking correctness depends on `src_sg`, `dst_sg`, skip offsets, `total_sent`, and `src_sent` staying synchronized across callbacks.
- AEAD fallback path calls into fallback ciphers for hardware limitations such as zero-length GCM/CCM payloads, unsupported CCM tag sizes on SPU-M, NSP zero-AAD CCM, RFC4106/RFC4543 assoc length constraints, and max payload overflow.
- Invalid ICV is converted to `-EBADMSG`, but destination buffers may already contain hardware-produced output; callers must honor AEAD failure semantics.
- HMAC behavior differs between SPU-M and SPU2, with SPU-M relying on software outer hash and generated ipad/opad.
- Mailbox send retry only sleeps when request flags allow sleeping; atomic-context requests may fail quickly on `-ENOBUFS`.
- Error cleanup must free per-chunk mailbox SG allocations exactly once. `spu_chunk_cleanup()` zeroes the message after freeing to make repeated cleanup harmless.
- Algorithm registration is large and partially conditional; missed `registered` state updates could break remove or error unwind.

## Test Signals

Test with crypto manager self-tests for all registered algorithms on each compatible hardware subtype. Add focused tests for multi-chunk CBC encrypt/decrypt IV chaining, CTR counter advancement, XTS tweak-in-payload variants, unaligned/scattered SG lists, non-final hash updates with partial blocks, hash export/import, SPU2 zero-length hash software fallback, HMAC keys longer than block size, GCM/CCM zero-length fallback, CCM unsupported auth sizes on SPU-M, RFC4106/RFC4543 assoc lengths 16/20 and invalid lengths, invalid ICV returning `-EBADMSG`, mailbox `-ENOBUFS` retry behavior with and without MAY_SLEEP, conditional SHA3 registration on SPU2 v2, and clean module removal after active sessions drain.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/cipher.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/bcm/cipher.h

## Purpose

This header defines the shared constants, algorithm descriptors, per-transform contexts, per-request contexts, hardware callback table, and global device-private structure for the Broadcom SPU crypto driver. `cipher.c` uses these declarations to register algorithms, construct mailbox messages, track request progress, and call SPU-M/SPU2-specific helper code.

## Important APIs, Types, and Functions

- Constants such as `MAX_SPUS`, `MAX_KEY_SIZE`, `MAX_IV_SIZE`, `MAX_DIGEST_SIZE`, `MAX_ASSOC_SIZE`, `SPU_MSG_ALIGN`, and `SPU_MB_RETRY_MAX` bound hardware instances, key/IV/digest storage, AEAD AAD size, alignment, and mailbox retry behavior.
- `enum op_type`, `enum spu_spu_type`, and `enum spu_spu_subtype` classify operation statistics and hardware generations.
- `struct iproc_alg_s` wraps a `skcipher_alg`, `ahash_alg`, or `aead_alg` with SPU cipher/auth metadata, auth ordering, and a `registered` flag.
- `struct spu_msg_buf` groups all per-request DMA/message fragments: request headers, IV/counter, digest, request padding, TX/RX status, skcipher XTS update/tweak, and AEAD GCM/AAD scratch buffers.
- `struct iproc_ctx_s` is the per-tfm state: encryption/auth keys, salt placement, IV, digest size, algorithm pointer, cipher/auth parameters, max payload, fallback AEAD, HMAC pads, cached request header, response header length, shash fallback, and RFC4543 flag.
- `struct spu_hash_export_s` is the compact exported hash state used by ahash export/import.
- `struct iproc_reqctx_s` tracks one crypto request across async mailbox callbacks, including parent request, selected context and channel, byte counters, source/destination SG cursors, AEAD assoc pointer, mailbox message, IV/counter, hash carry, incremental digest, and embedded AEAD fallback request.
- `struct spu_hw` is the hardware abstraction table. Its function pointers cover message dumping, max payload calculation, response length parsing, padding calculation, AEAD IV handling, hash type/digest sizing, request creation, cipher header init/finish, status processing, CCM IV update, and word alignment.
- `struct bcm_device_private` is the global platform state exported as `iproc_priv`.

## Control Flow

The header itself has no executable control flow, but it defines the data model used by `cipher.c`. Probe fills `bcm_device_private.spu` and mailbox fields. Crypto tfm init fills `iproc_ctx_s` from an `iproc_alg_s` entry. Request enqueue initializes `iproc_reqctx_s` cursors and counters. Hardware-specific functions in `spu_hw` are selected once based on device tree subtype and are then used by all request-building and response-parsing paths.

## State and Persistence Behavior

All structures are runtime-only. Transform state persists while a kernel crypto tfm exists and may contain key material, fallback handles, HMAC pads, salts, and cached SPU headers. Request state persists until the async mailbox operation completes. Exported hash state is intentionally small and excludes transient message buffers. Global counters and mailbox channel arrays persist for the platform device lifetime.

## Dependencies and Integration Points

The header includes Linux atomics, mailbox client and Broadcom message definitions, crypto AES/ARC4/GCM/SHA headers, internal hash/skcipher APIs, AEAD APIs, and SPU generation headers `spu.h`, `spum.h`, and `spu2.h`. It is the contract between `cipher.c`, utility code, and hardware-specific SPU message implementations.

## Risks and Edge Cases

- Fixed-size buffers must remain large enough for every algorithm registered in `cipher.c`; adding algorithms with larger keys, IVs, digests, or AAD requirements requires revisiting constants.
- `MAX_ASSOC_SIZE` caps AEAD associated data at 512 bytes in the hardware path.
- `struct spu_msg_buf` can contain sensitive material and is embedded in request contexts; debug dumps or use-after-free bugs would be security-sensitive.
- `struct spu_hw` callbacks must all be populated consistently for each hardware generation before requests can run.
- The global `extern struct bcm_device_private iproc_priv` couples all code to a single device instance.
- Hash export state size is constrained by crypto API expectations, so adding fields to `spu_hash_export_s` needs care.

## Test Signals

Compile coverage should catch missing callback declarations and structure size issues across SPU-M and SPU2 builds. Runtime tests should verify that request sizes fit buffers, AEAD AAD over 512 bytes is rejected, hash export/import restores counters and carry data, per-generation callback tables are fully populated, and debug/stat counters in `bcm_device_private` update as operations complete.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/bcm/cipher.h -->
