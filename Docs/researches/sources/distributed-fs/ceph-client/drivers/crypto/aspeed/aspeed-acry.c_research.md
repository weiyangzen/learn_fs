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
