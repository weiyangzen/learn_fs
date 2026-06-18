# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-cipher.c

## Purpose

`sun8i-ss-cipher.c` implements AES and 3DES ECB/CBC skcipher acceleration for the Allwinner A80/A83T Security System, using fallback skcipher providers for shapes the SS DMA engine cannot process.

## Important APIs, Types, And Functions

Key functions are `sun8i_ss_need_fallback()`, `sun8i_ss_cipher_fallback()`, `sun8i_ss_setup_ivs()`, `sun8i_ss_cipher()`, `sun8i_ss_handle_cipher_request()`, `sun8i_ss_skencrypt()`, `sun8i_ss_skdecrypt()`, `sun8i_ss_cipher_init()`, `sun8i_ss_cipher_exit()`, `sun8i_ss_aes_setkey()`, and `sun8i_ss_des3_setkey()`.

## Control Flow

Encrypt/decrypt zero the request context, set direction, reject zero or non-16-byte lengths, too many SGs, unaligned offsets, non-16-byte SG chunks, and mismatched source/destination SG layouts to fallback. Hardware requests select a flow, queue to that flow's crypto engine, map the key and optional IVs, map source/destination SGs, translate each segment into `t_src`/`t_dst` word lengths, and call `sun8i_ss_run_task()`. CBC IV handling precomputes per-SG IVs for decrypt and updates the caller IV from the last ciphertext block or saved decrypt IV.

## State And Persistence Behavior

TFM state stores the key, key length, SS device, and fallback TFM. Request state stores mapped source/destination entries, key and IV DMA addresses, method, mode, direction, flow, and fallback request. Per-flow IV and backup buffers are allocated by the core and scrubbed after use.

## Dependencies And Integration Points

It depends on `sun8i-ss-core.c` for engine queues, register programming, runtime PM references held by TFM init, and algorithm templates. It uses scatterwalk helpers, DMA mapping, skcipher internals, and fallback algorithm registration through `CRYPTO_ALG_NEED_FALLBACK`.

## Risks And Test Signals

Risks include stale `rctx->niv` causing IV unmap issues, exact SG-layout constraints pushing many users to fallback, IV update mistakes for in-place decrypt, key DMA lifetime errors, and hardware length units in words. Test AES/3DES ECB/CBC known vectors, in-place and out-of-place CBC, multi-SG boundaries, fallback counters, invalid key lengths, unaligned buffers, and concurrent two-flow operation.
