# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl-cipher.c

## Purpose

`amlogic-gxl-cipher.c` implements AES ECB/CBC skcipher acceleration for the Amlogic GXL crypto block, with fallback for zero-length and scatterlist shapes the descriptor engine cannot process.

## Important APIs, Types, And Functions

Key functions are `get_engine_number()`, `meson_cipher_need_fallback()`, `meson_cipher_do_fallback()`, `meson_cipher()`, `meson_handle_cipher_request()`, `meson_skencrypt()`, `meson_skdecrypt()`, `meson_cipher_init()`, `meson_cipher_exit()`, and `meson_aes_setkey()`. The hardware path fills `struct meson_desc` entries in a per-flow coherent descriptor list.

## Control Flow

Encrypt/decrypt set direction, fallback if source/destination SG counts differ, descriptor budget is exceeded, segments are not 16-byte aligned/length, offsets are not word aligned, or lengths differ. Hardware requests select a flow and queue to its crypto engine. `meson_cipher()` creates a DMA buffer containing key and optional IV, emits two key descriptors plus optional IV descriptor, maps SGs, emits data descriptors with mode, blockmode, direction, owner, and last bits, starts the flow by writing descriptor-list physical address to the flow register, waits for IRQ completion, unmaps DMA, and updates the caller IV from the last ciphertext block or saved decrypt IV.

## State And Persistence Behavior

TFM state stores copied key, key length, key mode, device pointer, and fallback TFM. Request state stores direction, selected flow, and fallback request. Per-flow descriptor memory and completion status persist in `meson_dev`. The bus clock remains enabled for the lifetime of the probed device; no runtime PM is implemented.

## Dependencies And Integration Points

It depends on `amlogic-gxl-core.c` for flow allocation, IRQs, algorithm registration, and crypto-engine queues. It uses CryptoAPI skcipher internals, scatterwalk, DMA mapping, and Amlogic descriptor constants from `amlogic-gxl.h`.

## Risks And Test Signals

Risks include descriptor count assumptions for key/IV, IV size vs cryptlen validation, missing DMA unmap on some early mapping failures, no runtime PM, reliance on equal SG layouts, and timeout at 500 ms. Test AES ECB/CBC vectors, in-place and out-of-place requests, multi-SG layouts, fallback counters, IV update behavior, DMA API debugging, and IRQ timeouts.
