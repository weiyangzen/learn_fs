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
