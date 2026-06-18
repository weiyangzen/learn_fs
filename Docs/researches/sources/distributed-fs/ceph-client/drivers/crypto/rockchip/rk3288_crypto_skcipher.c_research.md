# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_skcipher.c

## Purpose
This file implements the RK3288 crypto engine skcipher algorithms for AES, DES, and 3DES in ECB and CBC modes. It is the symmetric-cipher request layer for the Rockchip crypto driver: it validates request shape, routes unsupported requests to a software fallback, programs hardware registers, drives block DMA, maintains CBC IV semantics across scatterlist segments, and registers `skcipher_engine_alg` instances through shared `rk_crypto_tmp` descriptors declared in the Rockchip crypto core.

## Important APIs, types, and functions
The exported objects are `rk_ecb_aes_alg`, `rk_cbc_aes_alg`, `rk_ecb_des_alg`, `rk_cbc_des_alg`, `rk_ecb_des3_ede_alg`, and `rk_cbc_des3_ede_alg`. Their `base` members expose Linux Crypto API names such as `ecb(aes)`, `cbc(aes)`, `ecb(des)`, and `cbc(des3_ede)`, while their engine operation points to `rk_cipher_run()`.

Key setup is handled by `rk_aes_setkey()`, `rk_des_setkey()`, and `rk_tdes_setkey()`. AES accepts 128, 192, and 256 bit keys, DES uses `verify_skcipher_des_key()`, and 3DES uses `verify_skcipher_des3_key()`. Each setter stores the hardware key in `struct rk_cipher_ctx` and forwards the key to `ctx->fallback_tfm`.

Request entry points such as `rk_aes_cbc_encrypt()`, `rk_des3_ede_cbc_decrypt()`, and the ECB variants only set `struct rk_cipher_rctx::mode`, including `RK_CRYPTO_DEC` for decrypt, then call `rk_cipher_handle_req()`. `rk_cipher_tfm_init()` allocates a fallback skcipher with `CRYPTO_ALG_NEED_FALLBACK` and expands request size to include both `struct rk_cipher_rctx` and fallback request storage. `rk_cipher_tfm_exit()` wipes the key and frees the fallback.

## Control flow
`rk_cipher_handle_req()` first calls `rk_cipher_need_fallback()`. Hardware is bypassed for empty requests, unaligned source or destination offsets, segment lengths not divisible by the cipher block size, or source/destination scatterlists whose corresponding segment lengths differ. Counters such as `stat_fb_align`, `stat_fb_len`, `stat_fb_sgdiff`, and `stat_fb` are updated on fallback paths.

Hardware requests are sent to the device-wide `crypto_engine` from `get_rk_crypto()`. `rk_cipher_run()` is the engine callback. It resumes runtime PM, records request statistics, snapshots CBC decrypt IV material, and then iterates over matching source/destination scatterlist entries. Each segment is DMA-mapped, `rk_cipher_hw_init()` programs AES or TDES control/key/IV/byteswap registers, `crypto_dma_start()` writes BRDMA/BTDMA addresses and starts the block, and the code waits up to two seconds for `rkc->complete`. On success it unmaps DMA and advances the IV for the next scatterlist entry. On timeout it reports `-EFAULT`; on DMA mapping errors it returns `-EINVAL`.

## State and persistence behavior
Persistent transform state is the raw key, key length, and fallback transform in `struct rk_cipher_ctx`. Per-request state is the hardware mode, device pointer, backup IV, and fallback request storage in `struct rk_cipher_rctx`. Device state lives in `struct rk_crypto_info`: MMIO base, completion, status, request counters, runtime PM device, and crypto engine. No disk persistence exists. Sensitive key material is zeroed on transform exit and decrypt backup IVs are wiped after use.

## Dependencies and integration points
This file depends on the Linux Crypto API skcipher and crypto engine layers, DMA mapping, runtime PM, scatterwalk helpers, DES key verification helpers, and Rockchip-local register definitions from `rk3288_crypto.h`. Integration with the platform driver occurs through `get_rk_crypto()`, the shared engine, IRQ completion state, and registration of the `rk_crypto_tmp` templates elsewhere in the Rockchip driver.

## Risks
The fast path requires tightly paired scatterlists; otherwise fallback is frequent. `rk_cipher_need_fallback()` walks source and destination together but does not explicitly verify that the remaining total length is covered if one list ends early, so tests should cover malformed or short SG chains. Error handling after mapping failures has subtle labels: the path after a destination map failure unmaps source via `theend_sgs`, while the in-place path should avoid double-unmap assumptions. The two-second blocking wait in the engine worker makes interrupt delivery and status setting critical. IV handling across multi-entry CBC decrypt depends on backing up the last ciphertext block before overwrite.

## Test signals
Useful signals include Crypto API selftests for AES/DES/3DES ECB and CBC with 128/192/256 bit AES keys, weak DES/3DES key rejection, zero-length behavior, unaligned offsets, mismatched source/destination SG segment sizes, in-place versus out-of-place operation, multi-segment CBC IV propagation, runtime PM resume failures, DMA map failures, and forced IRQ timeout. Fallback counters should increase for alignment and length cases, while hardware request counters should increase only for aligned block-sized requests.
