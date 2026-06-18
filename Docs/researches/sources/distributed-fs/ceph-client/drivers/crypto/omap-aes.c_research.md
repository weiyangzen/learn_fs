## sources/distributed-fs/ceph-client/drivers/crypto/omap-aes.c

Purpose: implements the TI OMAP AES platform driver and Crypto API engine integration for AES ECB/CBC/CTR skciphers and, on OMAP4-class pdata, GCM AEAD algorithms implemented in `omap-aes-gcm.c`.

Important types and APIs: global `dev_list` provides round-robin device selection through `omap_aes_find_dev`. Core hardware helpers include `omap_aes_hw_init`, `omap_aes_write_ctrl`, DMA trigger/stop functions, `omap_aes_crypt_dma_start`, `omap_aes_crypt_dma`, and the PIO IRQ handler. Skcipher lifecycle functions include `omap_aes_prepare_req`, `omap_aes_crypt_req`, `omap_aes_crypt`, setkey/init/exit, and mode wrappers. Probe/remove register engine algorithms based on per-SoC `struct omap_aes_pdata`.

Control flow: probe obtains OF or platform resources, maps registers, enables runtime PM, reads hardware revision, initializes DMA or PIO fallback IRQ mode, adds the device to the global list, starts a crypto engine, and registers skcipher and optional AEAD engine algorithms. A skcipher request below `aes_fallback_sz` uses software fallback. Larger requests select a device, transfer to the crypto engine, align/copy input/output SGs as needed, write key/IV/control registers, map DMA SGs, submit DMA in/out descriptors, and trigger hardware. Completion work unmaps DMA, stops hardware DMA, cleans copy buffers, updates IV for CBC/CTR, finalizes the request, and autosuspends.

State and persistence: runtime state includes device list, per-device engine queue, DMA channels, SG pointers, mode flags, copy flags, fallback threshold, queue length sysfs setting, and runtime PM status. Transform state stores key material and fallback cipher. Sysfs attributes `fallback` and `queue_len` persist only until reboot/module unload.

Dependencies: platform/OF matching for `ti,omap2-aes`, `ti,omap3-aes`, `ti,omap4-aes`; DMA engine, runtime PM, crypto engine, OMAP crypto alignment helpers, `omap-aes.h` register/pdata definitions, and `omap-aes-gcm.c` AEAD callbacks.

Risks: `omap_aes_remove` assumes `aead_algs_info` is non-null, which is risky for OMAP2/3 pdata without AEAD algorithms. `omap_aes_setkey` ignores fallback setkey failure and returns success, which could mask unusable fallback state. DMA/PIO paths share device fields and must be serialized by the crypto engine. Sysfs queue length updates all devices under locks but affect active admission behavior. Runtime PM get/put balance must hold across all error paths.

Test signals: skcipher vectors for ECB/CBC/CTR, small-request fallback threshold behavior, invalid block sizes, key sizes 128/192/256, DMA and PIO modes, SG alignment/copy cleanup, IV update for CBC/CTR, sysfs fallback and queue_len changes, probe/remove on OMAP2/3/4 pdata including no-AEAD remove, runtime suspend/resume, and AEAD registration through OMAP4.
