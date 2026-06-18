<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-des.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-des.c

Purpose: implements OMAP DES and 3DES ECB/CBC hardware acceleration as asynchronous skcipher algorithms backed by DMA when available and by IRQ-driven PIO otherwise.

Important APIs and functions: `omap_des_setkey()` and `omap_des3_setkey()` validate DES/3DES keys and store little-endian key words. `omap_des_crypt()` validates block-aligned request length, sets request mode flags, and enqueues through the crypto engine. `omap_des_crypt_req()` chooses a device, prepares SGs with `omap_crypto_align_sg()`, programs keys/IV/control via `omap_des_write_ctrl()`, and starts DMA/PIO. `omap_des_done_task()` handles DMA unmap/stop, copy cleanup, CBC IV readback, and request finalization.

Control flow: probe maps registers, enables runtime PM, reads hardware revision, requests DMA channels, optionally falls back to IRQ PIO, adds the device to a global list, starts a one-slot crypto engine, and registers four skcipher algorithms. DMA submission maps source/destination SGs, configures both slave channels to the DES data register, starts the hardware trigger, and completes from the TX callback. PIO alternates DATA_IN and DATA_OUT IRQs per block.

State and persistence: global `dev_list` and `list_lock` select the first available device and cache it in `struct omap_des_ctx`. Device state carries active request, copy buffers, DMA channels, runtime PM flags, and counters. Transform contexts persist key material and cached device pointer.

Dependencies and integration: Linux platform driver/OF match `ti,omap4-des`, DMAengine channels `rx`/`tx`, crypto engine skcipher registration, runtime PM, OMAP common SG helpers, and DES key verification helpers.

Risks and test signals: `ctx->dd` caching can bind transforms to a removed device unless lifecycle ordering is correct. In-place requests force input copy, so cleanup must run on every path. PIO path uses `BUG_ON()` for SG state assumptions. Test DES/3DES ECB/CBC known vectors, DMA and no-DMA probe, unaligned SGs, in-place requests, runtime suspend/resume, removal while idle, and DMA error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-des.c -->
