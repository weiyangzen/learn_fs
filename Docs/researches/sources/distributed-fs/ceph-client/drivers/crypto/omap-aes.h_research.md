<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.h

Purpose: declares the OMAP AES hardware accelerator register map, mode flags, platform-data contract, request/device contexts, and cross-file entry points used by the OMAP AES skcipher and GCM implementation.

Important APIs and types: register macros derive key, IV, control, data, tag, IRQ, and DMA-mask offsets from `struct omap_aes_pdata`; flags describe encrypt, CBC, CTR, GCM, RFC4106-GCM, copy state, and fast paths. `struct omap_aes_ctx` stores AES key material, RFC4106 nonce, and skcipher fallback; `struct omap_aes_gcm_ctx` adds an expanded AES key; `struct omap_aes_reqctx` stores per-request mode, IV, tag, and fallback request. `struct omap_aes_dev` owns MMIO, crypto engine, queues, DMA channels, scatterlists, copy buffers, counters, and platform quirks.

Control flow and integration: callers set per-request flags, locate a device with `omap_aes_find_dev()`, program control through `omap_aes_write_ctrl()`, and start/stop DMA with `omap_aes_crypt_dma_start()`/`omap_aes_crypt_dma_stop()`. AEAD paths use the GCM-specific setkey, authsize, encrypt/decrypt, DMA callback, and engine request handler prototypes declared here.

State and persistence: transform contexts persist keys and fallback objects; device state persists queue, DMA, MMIO, and copy-state flags across requests. Request state is transient and must keep the fallback request last.

Dependencies: Linux crypto engine, AEAD/skcipher APIs, DMAengine, scatterlists, OMAP platform data, and AES constants.

Risks and test signals: register offsets and bit meanings are SoC-specific; wrong flags can corrupt IV/tag handling or DMA enablement. Test AES CBC/CTR/GCM/RFC4106 vectors, fallback paths, unaligned scatterlists, runtime PM, DMA callbacks, and probe/remove with each compatible platform data set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.h -->
