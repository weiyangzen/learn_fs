## sources/distributed-fs/ceph-client/drivers/crypto/omap-aes-gcm.c

Purpose: implements OMAP AES GCM AEAD request handling for `gcm(aes)` and `rfc4106(gcm(aes))`, sharing device selection, DMA, register programming, and engine integration with `omap-aes.c`.

Important APIs: queue and completion helpers are `omap_aes_gcm_handle_queue`, `omap_aes_gcm_crypt_req`, `omap_aes_gcm_finish_req`, `omap_aes_gcm_dma_out_callback`, and `omap_aes_gcm_done_task`. Request setup is `omap_aes_gcm_copy_buffers` and `omap_aes_gcm_prepare_req`. Public crypto callbacks include encrypt/decrypt wrappers, RFC4106 wrappers, setkey/authsize functions, and `omap_aes_gcm_cra_init`.

Control flow: encrypt/decrypt wrappers synthesize IVs, precompute E(K, J0) into `rctx->auth_tag`, validate RFC4106 AAD length, and enqueue via the shared crypto engine. The engine calls `omap_aes_gcm_prepare_req`, which aligns/copies AAD and payload into DMA-friendly SG lists, assigns device state, and writes AES control registers. DMA completion reads hardware tag registers, XORs with the precomputed tag and input tag for decrypt, cleans temporary SG buffers, copies auth tags on encrypt, checks decrypt tag mismatch, finalizes the AEAD request, and autosuspends the device.

State and persistence: per-request `omap_aes_reqctx` stores mode flags, synthetic IV, and auth tag scratch. Device state stores `aead_req`, SG pointers, total payload length, associated-data length, auth size, and flags. No persistent state exists beyond transform key/nonce in `omap_aes_gcm_ctx`.

Dependencies: `omap-aes.c` exports `omap_aes_find_dev`, `omap_aes_write_ctrl`, DMA start/stop, and GCM DMA callback hookup. Uses OMAP crypto SG alignment helpers, AES software key schedule for J0 encryption, crypto IPsec/GCM authsize validators, DMA engine APIs, runtime PM, and scatterwalk copy helpers.

Risks: RFC4106 subtracts 8 from assoclen in multiple paths, so validation order is critical. Zero-length AAD+payload returns a tag without hardware DMA and must be correct. Decrypt tag verification checks whether XOR result bytes are nonzero; it should remain constant-time enough for kernel AEAD expectations. SG cleanup must mirror all copy paths to avoid leaks or data corruption. `sg_arr` stack reuse around `scatterwalk_ffwd` is delicate.

Test signals: GCM and RFC4106 AEAD vectors, empty payload/AAD case, AAD-only and payload-only cases, authsize validation, decrypt bad-tag rejection, in-place and out-of-place SGs, unaligned SGs requiring copies, DMA and PIO-not-used interactions through shared driver, and runtime PM completion.
