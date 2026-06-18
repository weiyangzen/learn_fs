# subset-b-001214 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-acry.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-acry.c

## Purpose

`aspeed-acry.c` is the AST2600 ACRY asymmetric crypto driver. It registers an asynchronous kernel-only `rsa` akcipher implementation backed by the hardware RSA engine, with software fallback for modulus sizes beyond the 4096-bit hardware limit. The driver owns the ACRY MMIO block, an SRAM result window, a coherent DMA command/input buffer, an AHBC syscon gate used to switch SRAM protection, and a crypto-engine queue for serialized RSA operations.

## Important APIs, Types, And Functions

Core state is `struct aspeed_acry_dev`, `struct aspeed_acry_ctx`, and `struct aspeed_acry_alg`. The request path is `aspeed_acry_rsa_enc()` / `aspeed_acry_rsa_dec()` -> `aspeed_acry_handle_queue()` -> `aspeed_acry_do_request()` -> `aspeed_acry_rsa_trigger()`. `aspeed_acry_rsa_ctx_copy()` encodes exponent and modulus into the hardware SRAM word layout, while `aspeed_acry_rsa_sg_copy_to_buffer()` and `aspeed_acry_rsa_transfer()` translate between crypto scatterlists and the engine byte order. Key APIs parse DER public/private keys with `rsa_parse_pub_key()` / `rsa_parse_priv_key()`, cache `n/e/d`, and allocate a `CRYPTO_ALG_NEED_FALLBACK` akcipher.

## Control Flow

Probe maps control registers and SRAM resources, requests the IRQ, enables the clock, obtains the AHBC regmap from `aspeed,ahbc`, starts a crypto engine, initializes the tasklet, puts ACRY data memory in AHB CPU mode, builds SRAM index maps, allocates the coherent buffer, and registers `aspeed-rsa`. A request copies input, modulus, and exponent/private exponent into the DMA buffer, writes DMA base, length, and key-bit lengths, protects SRAM for engine access, unmasks `ACRY_RSA_ISR`, selects SRAM/DMA engine mode, and triggers RSA. The IRQ clears status, stops the engine, and schedules the tasklet; the tasklet copies the SRAM result back to the destination scatterlist and finalizes the akcipher request.

## State And Persistence Behavior

Per-transform state stores parsed RSA key material and fallback tfm. Per-device state stores the current request, busy flag, coherent buffer, SRAM mapping tables, crypto engine, and tasklet. Hardware state is transient for each operation: trigger, DMA command, source base, length, key lengths, interrupt mask/status, and AHBC SRAM protection are rewritten for every request. Key copies are freed with `kfree_sensitive()`, and the shared DMA buffer is wiped after transfer. The static temporary arrays used for data staging are not per-request objects, so the crypto-engine serialization is part of the safety model.

## Dependencies And Integration Points

The driver integrates with platform/OF matching for `aspeed,ast2600-acry`, Linux akcipher and crypto-engine APIs, RSA key parsers, DMA coherent memory, scatterwalk helpers, clock framework, IRQ/tasklet completion, MFD syscon/regmap, and the AHBC protection bit `REGION_ACRYM`. Fallback uses the same algorithm name through the generic crypto API with `CRYPTO_ALG_NEED_FALLBACK`.

## Risks And Test Signals

Risks include wrong SRAM index mapping, endian or leading-zero mistakes when computing bit lengths, failure to clear sensitive DMA/key data, busy-request assumptions around static buffers, result truncation handling when `dst_len` is too small, and AHBC protection not being restored on error paths. Test with crypto selftests for RSA encrypt/decrypt at 1024/2048/4096 bits and above-4096 fallback, invalid public/private keys, short destination buffers, concurrent async requests, driver unbind, IRQ completion, and fault injection around AHBC/regmap/DMA allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-acry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace-crypto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace-crypto.c

## Purpose

`aspeed-hace-crypto.c` implements the symmetric cipher half of the Aspeed HACE driver. It registers asynchronous kernel-only AES, DES, and 3DES skcipher algorithms for AST2500 and AST2600, using the HACE crypto engine and software fallback for unsupported or malformed requests. AST2500 uses a coherent bounce buffer, while AST2600 can drive hardware scatter-gather descriptors for source and destination.

## Important APIs, Types, And Functions

The file centers on `struct aspeed_cipher_ctx`, `struct aspeed_cipher_reqctx`, and the shared `struct aspeed_engine_crypto` from `aspeed-hace.h`. `aspeed_crypto_do_request()` is the crypto-engine callback. `aspeed_hace_skcipher_trigger()` prepares the context/key/IV area and dispatches to `aspeed_sk_start()` or `aspeed_sk_start_sg()`. `aspeed_aes_crypt()` and `aspeed_des_crypt()` validate mode lengths and construct command bits; `aspeed_aes_setkey()` and `aspeed_des_setkey()` validate/cache keys and configure fallbacks. Registration exports ECB/CBC AES/DES/3DES on all versions and CTR AES/DES/3DES on AST2600.

## Control Flow

Encrypt/decrypt callbacks fill `rctx->enc_cmd` and queue the request. The crypto-engine worker marks the hardware busy and calls the selected start function. The trigger writes the context DMA address, copies IVs for CBC/CTR-like modes, copies keys after the IV area, enables interrupts, and starts either bounce-buffer or SG processing. Bounce mode copies input sg data into `cipher_addr`, programs source/destination to the same DMA buffer, and copies results back on completion. SG mode maps the caller scatterlists, builds HACE SG descriptors with the last bit in the final length field, programs hardware, then unmaps on interrupt-driven completion.

## State And Persistence Behavior

Transform state stores the key, key length, fallback skcipher, and start callback. Request state stores command bits and mapped sg counts. The device crypto engine stores one active request, coherent context buffer, source descriptor/input buffer, optional AST2600 destination descriptor buffer, resume callback, and busy flag. CBC/DES IV state is updated from the hardware context buffer when the request completes. DMA mappings are per request and are released in the resume path or on setup failure.

## Dependencies And Integration Points

The code depends on the parent HACE platform driver for MMIO, IRQ, DMA buffers, version selection, and crypto-engine allocation. It integrates with Linux skcipher/crypto-engine APIs, DES/AES key validation, DMA mapping, scatterlist helpers, and the HACE register/command definitions in `aspeed-hace.h`. Software fallback is allocated by algorithm name and used for AST2500 zero-length or block-unaligned requests.

## Risks And Test Signals

Risks include descriptor overflow relative to the fixed 0xa000 coherent buffers, incomplete unmap on SG errors, AST2500 fallback behavior differing from AST2600, IV update offsets for DES versus AES, CTR edge cases with non-block-sized input, and silent registration failures because register loops only log errors. Test with `tcrypt`/crypto selftests for AES/DES/3DES ECB/CBC/CTR, in-place and out-of-place SGs, unaligned lengths, zero-length requests, large fragmented scatterlists, fallback paths, and interrupt-with-no-busy warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace-crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace-hash.c

## Purpose

`aspeed-hace-hash.c` implements the hash half of Aspeed HACE. It exposes asynchronous SHA1, SHA224, and SHA256 on all supported HACE devices, plus SHA384 and SHA512 on AST2600, using hardware accumulation mode and software fallback for cases the hardware path cannot prepare. It manually tracks SHA byte counts and padding, because requests can arrive as streaming updates and finup/digest operations.

## Important APIs, Types, And Functions

Important state is `struct aspeed_sham_ctx`, `struct aspeed_sham_reqctx`, and `struct aspeed_engine_hash`. `aspeed_sham_init()`, `update()`, `finup()`, `digest()`, `export()`, and `import()` implement ahash callbacks. `aspeed_ahash_dma_prepare()` builds a linear DMA buffer for AST2500, while `aspeed_ahash_dma_prepare_sg()` builds AST2600 source SG descriptors and optional padding buffer descriptors. `aspeed_hace_ahash_trigger()` writes source, digest, key-buffer, length, and command registers. `aspeed_ahash_fallback()` replays the remaining request through a software ahash if hardware setup fails.

## Control Flow

Initialization selects algorithm flags, digest size, block size, IV size, and initial digest constants. Update/finup records the source sg, total length, offset, and final flag, then queues the request on the hash crypto engine. The engine prepare step selects linear or SG DMA preparation by SoC version. Hardware completion unmaps DMA state, decides whether another chunk is required, and either loops back into `aspeed_ahash_req_update()` or copies the final digest to `req->result` and finalizes the request. AST2600 SG mode appends a separate padding buffer for final blocks and marks the last SG descriptor with `HASH_SG_LAST_LIST`.

## State And Persistence Behavior

Request context preserves digest words, 128-bit byte count, source walk position, command bits, final flag, and DMA addresses. Export/import serializes digest plus byte count so the crypto API can suspend/resume partial hashes. The device hash engine stores one active request, coherent source/descriptor buffer, active DMA addresses/lengths, callbacks, and busy flag. Digest DMA is mapped bidirectionally for each hardware round and unmapped before continuing or finalizing.

## Dependencies And Integration Points

The file depends on `aspeed-hace.h`, crypto ahash and crypto-engine APIs, SHA constants, `memcpy_from_sglist()`, scatterwalk fallback, DMA mapping, and HACE hash registers. It is registered by the parent HACE platform driver and version-gates SHA384/SHA512 and SG mode to AST2600.

## Risks And Test Signals

Risks include padding/count mistakes for SHA512-family two-word lengths, final SG descriptor indexing when zero or truncated SG entries occur, digest DMA lifetime across multi-chunk requests, fallback import/export compatibility, and registration failure only being logged. Test with crypto selftests for all advertised digests, streaming update/final/export/import, short and exact-block messages, very large messages crossing chunk limits, fragmented sg lists, AST2500 linear and AST2600 SG paths, and injected DMA mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace.c

## Purpose

`aspeed-hace.c` is the parent platform driver for the Aspeed Hash and Crypto Engine. It owns the shared HACE register block, clock, IRQ, coherent DMA buffers, crypto-engine queues, and tasklets used by the separate hash and symmetric-cipher implementation files. It supports AST2500 (`aspeed,ast2500-hace`) and AST2600 (`aspeed,ast2600-hace`) and conditionally registers hash and crypto algorithms depending on Kconfig.

## Important APIs, Types, And Functions

`aspeed_hace_probe()` and `aspeed_hace_remove()` are the platform lifecycle. `aspeed_hace_irq()` clears `ASPEED_HACE_STS` and schedules the hash or crypto done tasklet based on `HACE_HASH_ISR` and `HACE_CRYPTO_ISR`. `aspeed_hace_hash_done_task()` and `aspeed_hace_crypto_done_task()` call the current engine resume callback. `aspeed_hace_register()` and `aspeed_hace_unregister()` dispatch to the hash and skcipher registration helpers declared in `aspeed-hace.h`.

## Control Flow

Probe allocates `struct aspeed_hace_dev`, records the hardware version from OF match data, maps resource 0, requests IRQ 0, gets and enables the device clock, allocates and starts two crypto-engine instances, initializes tasklets, allocates a hash source buffer, a cipher context buffer, a cipher source buffer, and on AST2600 a cipher destination SG buffer, then registers algorithms. Remove unregisters algorithms, exits the engines, kills tasklets, and disables the clock.

## State And Persistence Behavior

The driver keeps one persistent device object with MMIO base, clock, IRQ, hardware version, two crypto-engine handles, and per-engine state. DMA buffers are coherent and device-managed, so their lifetime is the platform device lifetime. Busy state lives in the per-engine flags and is checked by the ISR before scheduling a completion tasklet. Hardware status is acknowledged by writing back the value read from `ASPEED_HACE_STS`.

## Dependencies And Integration Points

It integrates with platform/OF probing, `devm_platform_get_and_ioremap_resource()`, IRQ/tasklet APIs, the common clock framework, DMA coherent allocation, the Linux crypto engine, and compile-time feature symbols `CONFIG_CRYPTO_DEV_ASPEED_HACE_HASH` and `CONFIG_CRYPTO_DEV_ASPEED_HACE_CRYPTO`. The child implementation files rely on its buffers and `version` field to choose AST2500 versus AST2600 behavior.

## Risks And Test Signals

Risks include error unwind calling `crypto_engine_exit()` on an unallocated second engine, algorithm registration failures not causing probe failure, interrupts arriving after unregister but before tasklet kill, missing reset of stale hardware state on probe, and fixed coherent buffer sizes constraining large SG descriptors. Test by probing both compatibles, enabling hash-only/crypto-only/both Kconfig variants, running crypto selftests, checking remove/unbind paths, injecting allocation/IRQ/clock failures, and verifying no "no active requests" warnings under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace.h

## Purpose

`aspeed-hace.h` is the shared hardware contract and internal interface for the Aspeed HACE hash and symmetric cipher drivers. It defines register offsets, command/status bits, SoC version identifiers, DMA buffer sizing, scatter-gather descriptor layout, per-engine runtime state, crypto transform/request contexts, and registration prototypes used by `aspeed-hace.c`, `aspeed-hace-crypto.c`, and `aspeed-hace-hash.c`.

## Important APIs, Types, And Functions

Important definitions include `ASPEED_HACE_*` register offsets, `HACE_CMD_*` cipher mode/key/interrupt/SG bits, `HASH_CMD_*` hash algorithm/control bits, SHA flag bits, and fixed coherent buffer sizes. `struct aspeed_sg_list` is the little-endian hardware SG descriptor. `struct aspeed_engine_hash` and `struct aspeed_engine_crypto` hold active request, DMA buffers, tasklet, busy flag, and resume callbacks. `struct aspeed_sham_reqctx`, `struct aspeed_cipher_ctx`, and `struct aspeed_cipher_reqctx` define per-request/per-transform crypto API state. `ast_hace_read()` and `ast_hace_write()` wrap MMIO.

## Control Flow

This header does not execute control flow, but it defines how callers program HACE: write source/destination/context/digest buffer addresses, data length, and command bits; receive status through `ASPEED_HACE_STS`; and use resume callbacks from IRQ tasklets to finish queued crypto-engine work. Version values distinguish AST2500 from AST2600 feature sets.

## State And Persistence Behavior

The structures distinguish device-lifetime state (`struct aspeed_hace_dev`), engine-lifetime DMA/tasklet state, transform-lifetime keys and fallback tfms, and request-lifetime offsets, counters, command bits, and digest buffers. Digest buffers are aligned for DMA. SG descriptors use little-endian length/address fields with high-bit end markers for hash and cipher code paths.

## Dependencies And Integration Points

The header pulls in AES, hash, SHA2, crypto-engine, interrupt, and Linux type definitions. It exposes the internal registration functions for optional hash and crypto compilation units and centralizes AST2500/AST2600 differences so the implementation files agree on register bits and buffer sizes.

## Risks And Test Signals

Risks include stale register bit definitions, buffer constants that are too small for descriptor-heavy requests, mismatched endian expectations in `aspeed_sg_list`, and context-layout assumptions shared by cipher completion and hardware. Test signals are compile coverage for all Kconfig combinations, sparse/endian checks on SG descriptors, and runtime selftests that exercise every command bit combination advertised by the algorithm tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-aes-regs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/atmel-aes-regs.h

## Purpose

`atmel-aes-regs.h` defines the MMIO register map and bit fields for the Atmel/Microchip AES hardware accelerator. It is consumed by `atmel-aes.c` to configure cipher direction, key size, block mode, DMA/manual transfer mode, GCM, XTS, padding, interrupt status, IV/key/data/tag registers, and hardware-version discovery.

## Important APIs, Types, And Functions

There are no functions or types. Important macros include `AES_CR_*` control bits, `AES_MR_*` mode fields for encryption/decryption, source mode, key size, ECB/CBC/OFB/CFB/CTR/GCM/XTS modes, CFB size, and countermeasure key/type fields; `AES_INT_*` interrupt bits; indexed accessors `AES_KEYWR(x)`, `AES_IDATAR(x)`, `AES_ODATAR(x)`, `AES_IVR(x)`, `AES_GHASHR(x)`, `AES_TAGR(x)`, `AES_GCMHR(x)`, `AES_TWR(x)`, and `AES_ALPHAR(x)`; and extended-mode padding/PLIP macros.

## Control Flow

The header drives control flow indirectly: the driver writes `AES_MR` before IV/key registers, uses `AES_IER`/`AES_IDR`/`AES_ISR` to wait for data and tag readiness, writes `AES_CR_START` or `AES_CR_SWRST` for operation control, and reads `AES_HW_VERSION` to select algorithm capabilities.

## State And Persistence Behavior

All state represented here is hardware state. Key, IV, input, output, GHASH, tag, tweak, and alpha registers are overwritten per request. Interrupt mask/status and mode registers persist until the driver disables or reprograms them.

## Dependencies And Integration Points

The macros rely on Linux `BIT()` for extended mode fields and match the AES IP register ABI used by platform devices compatible with `atmel,at91sam9g46-aes`. `atmel-aes.c` combines these values with crypto API mode flags.

## Risks And Test Signals

Risks are wrong offsets or bit masks causing silent cryptographic corruption, especially for GCM tag generation, XTS tweak registers, and PLIP/authenc mode. Test through AES ECB/CBC/CTR/GCM/XTS/authenc selftests, interrupt-status checks, and comparing capability decisions against `AES_HW_VERSION` values on real SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-aes-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-aes.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-authenc.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/atmel-authenc.h

## Purpose

`atmel-authenc.h` is the conditional internal API that lets the Atmel AES driver coordinate SPLIP/authenc processing with the Atmel SHA driver. It is compiled only when `CONFIG_CRYPTO_DEV_ATMEL_AUTHENC` is enabled and avoids exposing SHA internals directly to unrelated code.

## Important APIs, Types, And Functions

The header forward-declares `struct atmel_aes_dev` and opaque `struct atmel_sha_authenc_ctx`, defines `atmel_aes_authenc_fn_t` callbacks, and declares readiness, request-size, spawn/free, setkey, schedule, init, final, and abort helpers. These functions are implemented in `atmel-sha.c` and called from `atmel-aes.c` authenc mode. It includes crypto authenc/hash/SHA headers and `atmel-sha-regs.h` for mode constants.

## Control Flow

AES authenc starts by checking `atmel_sha_authenc_is_ready()`, spawning a SHA HMAC context for the desired algorithm, scheduling ownership of the SHA hardware, initializing SHA over associated data and ciphertext/plaintext length, transferring AES data in PLIP mode, then asking SHA to finalize and return the digest/tag through callbacks.

## State And Persistence Behavior

The header itself stores no state. Its API implies an opaque SHA authenc context per AES transform and an ahash request area embedded at the end of AES authenc request context. Callback parameters carry the AES device, error, and async-completion indication between the SHA and AES drivers.

## Dependencies And Integration Points

This is an internal cross-driver interface between `atmel-aes.c` and `atmel-sha.c`. It depends on the crypto authenc key format and SHA mode flags, and is compiled away when authenc support is disabled.

## Risks And Test Signals

Risks include ABI drift between declarations and `atmel-sha.c`, request-size mismatches because AES embeds an ahash request after its context, and callback ordering bugs that leave AES or SHA hardware busy. Test by building with and without `CONFIG_CRYPTO_DEV_ATMEL_AUTHENC`, probing AES before SHA to exercise defer, and running authenc HMAC-SHA1/SHA224/SHA256/SHA384/SHA512 CBC-AES selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-authenc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-ecc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/atmel-ecc.c

## Purpose

`atmel-ecc.c` registers a KPP implementation of `ecdh-nist-p256` backed by Microchip/Atmel ATECC508A-class I2C secure elements. The device generates and stores a random private key internally, returns the public key, and computes shared secrets using its ECDH command. Software fallback is used when the caller supplies its own private key or otherwise requests unsupported behavior.

## Important APIs, Types, And Functions

`struct atmel_ecdh_ctx` stores the selected I2C client, fallback KPP transform, generated public key, curve id, and fallback flag. `atmel_ecdh_set_secret()` decodes crypto ECDH parameters and either triggers on-device GenKey or configures fallback. `atmel_ecdh_generate_public_key()` returns the saved device-generated public key. `atmel_ecdh_compute_shared_secret()` builds asynchronous `atmel_i2c_work_data` and queues an ECDH command. Client load balancing uses `atmel_ecc_i2c_client_alloc()` and `tfm_count`.

## Control Flow

Module init initializes a global client list and registers an I2C driver. Probe calls the shared `atmel_i2c_probe()` sanity check, adds the client to the list, and registers the KPP algorithm. Transform init chooses the least-used I2C client and allocates fallback. `set_secret()` with an empty private key asks the device to generate a key in slot 2 and stores the returned public key. Shared-secret requests validate the peer public key length, allocate work, initialize an ECDH I2C command, enqueue it, and complete in `atmel_ecdh_done()` after copying the response to the destination sg.

## State And Persistence Behavior

The device persistently stores/generated private key material in `DATA_SLOT_2`; the driver stores only the returned public key in memory. Global state is a list of probed I2C clients protected by a spinlock and per-client active transform counters. Per-request I2C work is heap-allocated and freed on completion. Removing a busy client logs an emergency warning because the I2C remove path cannot fail and in-flight work may later touch freed memory.

## Dependencies And Integration Points

The driver depends on the shared Atmel I2C command layer, Linux KPP/ECDH crypto APIs, I2C device/OF matching for `atmel,atecc508a`, workqueues, scatterlist helpers, and crypto fallback transforms. It exports a higher-priority hardware-backed `ecdh-nist-p256` algorithm.

## Risks And Test Signals

Risks include global algorithm registration conflicts with multiple devices, lack of serialization between `set_secret()` and in-flight public/shared-secret operations as documented in the context comment, unsafe remove while transforms exist, fallback tfm substitution on the original request, and reliance on locked secure-element zones. Test with ECDH selftests, multiple I2C devices, fallback with caller-supplied private keys, invalid peer key sizes, async cancellation/unbind scenarios, and I2C error/status injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-ecc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/atmel-i2c.c

## Purpose

`atmel-i2c.c` is the shared transport and command-construction layer for Atmel/Microchip I2C crypto devices used by the ECC and SHA204A drivers. It builds device commands with CRC16, performs wake-command-delay-read-sleep transactions, verifies lock state during probe, and provides a per-CPU workqueue for asynchronous requests.

## Important APIs, Types, And Functions

Exported command builders include `atmel_i2c_init_read_config_cmd()`, `atmel_i2c_init_read_otp_cmd()`, `atmel_i2c_init_random_cmd()`, `atmel_i2c_init_genkey_cmd()`, and `atmel_i2c_init_ecdh_cmd()`. `atmel_i2c_send_receive()` is the synchronous transaction primitive. `atmel_i2c_enqueue()` and `atmel_i2c_flush_queue()` manage async work. `atmel_i2c_probe()` validates adapter support, bus speed, wake-token length, client-private data, and locked configuration/data zones.

## Control Flow

Command builders fill word address, opcode, parameters, count, CRC, expected execution time, and response size. `send_receive()` locks the client mutex, sends a wake token while ignoring NAK, waits the wake interval, reads wake status, sends the command, sleeps for the command-specific execution time, reads the response, sends sleep, unlocks, and decodes status/error bytes. Async work simply calls the synchronous primitive and invokes the caller callback.

## State And Persistence Behavior

Per-client state contains the I2C client pointer, list node, transaction mutex, precomputed all-zero wake token sized from bus clock, active transform count, and optional hwrng object. The module owns a global workqueue. Secure-element configuration, OTP, and data zones are persistent hardware state; probe rejects devices whose configuration or data/OTP zones are unlocked because secrets could be modified.

## Dependencies And Integration Points

The file depends on I2C core, ACPI/firmware bus-speed discovery, CRC16/bit reversal, delay/sleep APIs, workqueues, scatterlist copying for ECDH public keys, and exported symbols consumed by `atmel-ecc.c` and `atmel-sha204a.c`.

## Risks And Test Signals

Risks include imprecise fixed sleeps for command completion, status responses with unknown error IDs being ignored, failure to sleep the device on some error paths, wake-token sizing for unusual bus rates, async work executing after device removal, and security-sensitive lock-state assumptions. Test probe at valid/invalid I2C clock rates, locked/unlocked device configs, command CRC vectors, random/genkey/ecdh/read commands, concurrent async enqueue, and I2C NAK/timeout/status-error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/atmel-i2c.h

## Purpose

`atmel-i2c.h` is the shared protocol header for Atmel/Microchip I2C crypto secure elements. It defines packet sizes, opcodes, response formats, timing constants, secure-element zones, shared per-client/private work structures, and exported helper prototypes used by ECC and SHA204A drivers.

## Important APIs, Types, And Functions

Important types are `struct atmel_i2c_cmd`, `struct atmel_ecc_driver_data`, `struct atmel_i2c_client_priv`, and `struct atmel_i2c_work_data`. Constants describe command overhead, P-256 key sizes, response sizes, status bytes, lock-byte indexes, wake timing, max command execution times, and opcodes for ECDH, GenKey, Read, and Random. Prototypes expose probe, enqueue/flush, send/receive, and command initialization helpers.

## Control Flow

The header defines the structure that all command builders fill: word address, count, opcode, param1, param2, data/CRC, execution delay, and response size. Async users allocate `atmel_i2c_work_data`, set a client and command, then call `atmel_i2c_enqueue()` to run the transaction and invoke a callback.

## State And Persistence Behavior

Per-client state tracks serialized transport access through a mutex, the all-zero wake token, an active transform count used by ECC and SHA204A, and an embedded hwrng descriptor for SHA204A. Device persistence is modeled by constants for configuration, OTP, lock bytes, ECDH private key slot 2, and OTP zone sizing.

## Dependencies And Integration Points

The header depends on Linux hwrng/types and is shared by `atmel-i2c.c`, `atmel-ecc.c`, and `atmel-sha204a.c`. Its constants encode the secure-element protocol ABI and the crypto driver priority used by the ECC KPP algorithm.

## Risks And Test Signals

Risks include response-size constants getting out of sync with command payloads, packed-structure layout assumptions, hard-coded P-256/slot-2 behavior limiting flexibility, and wake/execute timing constants that may not cover all parts. Test by compiling all consumers, checking command byte layouts against datasheets, and exercising read/random/genkey/ecdh paths on supported devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha-regs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha-regs.h

## Purpose

`atmel-sha-regs.h` defines the MMIO register map and mode/interrupt bits for Atmel/Microchip SHA hardware. It is used by `atmel-sha.c` and by the authenc interface to configure SHA1/SHA224/SHA256/SHA384/SHA512, HMAC, DMA/PDC transfer mode, user-initialized hash values, and digest/input register access.

## Important APIs, Types, And Functions

There are no functions or types. Important macros include `SHA_REG_DIGEST(x)`, `SHA_REG_DIN(x)`, `SHA_CR_*` control bits, `SHA_MR_*` mode, algorithm, HMAC, UIHV, and dual-buffer fields, derived `SHA_FLAGS_*` algorithm/mode combinations, interrupt bits `SHA_INT_DATARDY`, `ENDTX`, `TXBUFE`, and `URAD`, message/byte count registers, version register, and PDC/DMA pointer/count/control/status registers.

## Control Flow

The SHA driver uses these constants to reset or start first blocks, restore intermediate hash state through UIHV/UIEHV, select manual/auto/PDC/IDATAR0 transfer mode, program message sizes for automatic padding/HMAC, wait for data-ready interrupts, and configure PDC transmit registers on older hardware.

## State And Persistence Behavior

All represented state is hardware state: mode, digest/input windows, message size, byte count, DMA pointer/count, interrupt masks, and version. Digest registers may contain intermediate state between streaming updates unless UIHV is available and used to restore contexts explicitly.

## Dependencies And Integration Points

The file relies on `GENMASK()`/bit constants from Linux includes pulled by consumers. It is the shared register ABI for platform devices compatible with `atmel,at91sam9g46-sha` and for AES authenc coordination.

## Risks And Test Signals

Risks include incorrect algorithm encodings, confusion between `SHA_MR_MODE_PDC` and `SHA_MR_MODE_IDATAR0`, UIHV bit misuse, and interrupt mask mismatches. Test through standalone SHA/HMAC selftests, authenc tests, PDC/DMA and CPU paths, UIHV restore on interleaved requests, and hardware-version capability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha204a.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha204a.c

## Purpose

`atmel-sha204a.c` is the I2C driver for Microchip/Atmel ATSHA204/ATSHA204A devices. It exposes the device random command through the Linux hwrng framework and exports the OTP zone through a read-only sysfs attribute. It uses the shared `atmel-i2c` transport for wake, command, read, status handling, and queued asynchronous random reads.

## Important APIs, Types, And Functions

`atmel_sha204a_rng_read()` implements blocking and nonblocking hwrng reads. `atmel_sha204a_rng_read_nonblocking()` keeps at most one queued random command by using `tfm_count` and `rng->priv` to hold completed work data. `atmel_sha204a_rng_done()` stores completed async work for the next read and decrements the in-flight count. `atmel_sha204a_otp_read()` reads one OTP word, and `otp_show()` concatenates the 64-byte OTP zone as hex. Probe registers hwrng and sysfs group after `atmel_i2c_probe()`.

## Control Flow

Probe validates the secure element through the shared I2C probe, initializes the embedded hwrng with quality 1, registers it with devm hwrng, and creates `/sys/.../atsha204a/otp`. Blocking hwrng reads synchronously issue a random command and copy response data. Nonblocking reads either return data from the previous completed work item and queue the next request, or allocate/queue the first work item and return zero bytes. Removal unregisters hwrng, flushes the shared I2C queue, removes sysfs, and frees any cached work.

## State And Persistence Behavior

Per-client state is inherited from `struct atmel_i2c_client_priv`, including the hwrng object and `tfm_count` reused as a one-operation in-flight guard. `rng->priv` temporarily owns an allocated `atmel_i2c_work_data` containing the last random response. OTP content is persistent device state and is read on demand. The hwrng quality is deliberately set to 1 because the hardware RNG is considered low entropy.

## Dependencies And Integration Points

The driver depends on the I2C core, hwrng framework, sysfs attributes, shared Atmel I2C command helpers, workqueues, and OF/I2C IDs for `atmel,atsha204` and `atmel,atsha204a`.

## Risks And Test Signals

Risks include low entropy despite hwrng exposure, stale `rng->priv` work data after errors, concurrent remove/read interactions, OTP sysfs reads blocking for many I2C transactions, and response copying including count/status bytes rather than only random payload. Test hwrng blocking/nonblocking reads, sysfs OTP output length/content, queue flushing on remove, I2C random/read failures, and behavior under repeated short hwrng reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha204a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-tdes-regs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/atmel-tdes-regs.h

## Purpose

`atmel-tdes-regs.h` defines the register map and bit fields for the Atmel/Microchip TDES/DES/XTEA hardware accelerator. It is a hardware definition header, not an algorithm implementation, and would be consumed by a TDES driver to configure mode, keys, IVs, data registers, interrupts, and PDC transfers.

## Important APIs, Types, And Functions

There are no functions or types. Important macros include `TDES_CR_*` control bits, `TDES_MR_*` fields for encrypt/decrypt, DES/TDES/XTEA selection, two-key versus three-key TDES, source mode, operation mode ECB/CBC/OFB/CFB, CFB size, countermeasure key/type fields, interrupt status bits, key/input/output/IV registers, XTEA round count register, version register, and PDC receive/transmit pointer/count/control/status registers.

## Control Flow

The header defines the values a driver would write when resetting or starting the block, configuring transfer mode, waiting for `TDES_INT_DATARDY` or DMA/PDC completion, loading keys and IVs, moving input/output data, and enabling/disabling PDC RX/TX.

## State And Persistence Behavior

All state is hardware-backed: mode, key, IV, data, interrupt, XTEA round, and PDC registers persist until reset or reprogramming. The header contains no software persistence or runtime allocation.

## Dependencies And Integration Points

The macros are tied to Atmel TDES IP and Linux consumers that include this header. The register layout mirrors patterns used by AES/SHA register headers, especially manual/auto/PDC transfer modes and shared interrupt semantics.

## Risks And Test Signals

Risks include wrong bit masks for TDES key mode, overlapping `TDES_TNPR/TNCR` and `TDES_RNPR/RNCR` aliases, and mode fields that silently corrupt cryptographic output if misprogrammed. Test through any consuming TDES driver with DES/2-key/3-key TDES/XTEA known-answer vectors, interrupt status handling, and PDC transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/atmel-tdes-regs.h -->
