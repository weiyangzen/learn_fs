# sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-aes.c

## Purpose
This file implements AES acceleration for the StarFive JH7110 crypto engine. It registers AES ECB/CBC/CTR skcipher algorithms and AES GCM/CCM AEAD algorithms, manages fallback transforms for unsupported request shapes, programs AES registers, moves payload through DMA, handles AAD/tag processing for AEAD, and finalizes requests through the shared crypto engine.

## Important APIs, types, and functions
The file uses shared `struct starfive_cryp_ctx`, `struct starfive_cryp_dev`, and `struct starfive_cryp_request_ctx` from `jh7110-cryp.h`. Register offsets cover AES key, IV, nonce, AAD length, message length, IV length, FIFO, and CSR fields. `FLG_MODE_MASK` and `FLG_ENCRYPT` encode request mode in `cryp->flags`.

Hardware setup functions include `starfive_aes_wait_busy()`, `starfive_aes_wait_keydone()`, `starfive_aes_wait_gcmdone()`, `starfive_aes_write_key()`, `starfive_aes_write_iv()`, `starfive_aes_ccm_init()`, and `starfive_aes_hw_init()`. DMA is configured through `starfive_aes_dma_init()`, `starfive_aes_dma_xfer()`, and `starfive_aes_map_sg()`. Engine callbacks are `starfive_aes_do_one_req()` for skcipher and `starfive_aes_aead_do_one_req()` for AEAD. Registration is via `starfive_aes_register_algs()` and `starfive_aes_unregister_algs()`.

## Control flow
Transform init finds a device with `starfive_cryp_find_dev()`, allocates a software fallback such as `ecb(aes-lib)`, `cbc(aes-lib)`, `ctr(aes-lib)`, `gcm_base(ctr(aes-lib),ghash-lib)`, or `ccm_base(ctr(aes-lib),cbcmac-aes-lib)`, and sizes request context to include fallback storage. Setkey validates AES key length, stores the key, and forwards it to the fallback.

Skey cipher wrappers set mode and encryption flags, reject non-block-aligned ECB/CBC lengths, run `starfive_aes_check_unaligned()`, and either fallback or enqueue to the crypto engine. The engine callback stores request pointers and lengths in `cryp`, initializes hardware, sets up DMA, maps SGs one segment at a time, handles split source/destination progression with `scatterwalk_ffwd()`, and finalizes the skcipher request. Completion reads updated IV for CBC/CTR.

AEAD wrappers additionally validate CCM IV format and always fallback for CCM decrypt because this hardware path cannot verify non-aligned CCM text. AEAD engine execution skips associated data using `scatterwalk_ffwd()`, copies incoming tags for decrypt, pads text with `sg_zero_buffer()` when needed, initializes hardware lengths, writes AAD through GCM nonce registers or CCM data FIFO, transfers payload by DMA, reads or verifies the authentication tag, and finalizes the AEAD request.

## State and persistence behavior
Per-device state in `starfive_cryp_dev` is reused for the active request: request pointer union, `assoclen`, `total_in`, `total_out`, tag buffers, auth size, flags, error, DMA completion, DMA configs, and side-channel mitigation flag. Per-transform state holds key bytes, key length, fallback transforms, and cached device pointer. Per-request context stores CSR images, SG pointers, total lengths, digest metadata shared with other algorithm files, and temporary AAD buffer pointer. No disk persistence exists. Fallback transforms are freed on transform exit; AAD buffers are allocated per AEAD request and freed before payload transfer.

## Dependencies and integration points
This file depends on the shared platform driver in `jh7110-cryp.c` for clocks, reset, DMA channels, engine allocation, and algorithm registration. It uses Linux DMAengine, crypto engine, scatterwalk, AEAD/skcipher internals, `crypto_gcm_check_authsize()`, and register definitions from `jh7110-cryp.h`.

## Risks
DMA error handling in `starfive_aes_map_sg()` can return after a destination map failure without unmapping a successfully mapped source in that iteration. The AEAD path uses `sg_dma_len(rctx->in_sg)` before DMA mapping in the `sg_zero_buffer()` length expression, which deserves scrutiny because `sg_dma_len` is normally valid after mapping. Hardware polling timeouts must propagate and leave the engine usable for later requests. AAD handling assumes enough allocated padding and correct CCM formatting. Device state is shared through `cryp->flags` and request unions, so crypto engine serialization is required for correctness.

## Test signals
Run AES ECB/CBC/CTR tests for 128/192/256 bit keys, block and partial CTR lengths, unaligned offset/length fallback, in-place and out-of-place SGs with unequal segment sizes, IV update after CBC/CTR, DMA timeout injection, and side-channel module parameter coverage. AEAD tests should cover GCM auth sizes, CCM auth sizes and IV L field validation, encrypt/decrypt with AAD lengths 0, short, block-sized, and multi-block, bad-tag detection, CCM decrypt fallback, empty plaintext with AAD, and SG padding behavior.
