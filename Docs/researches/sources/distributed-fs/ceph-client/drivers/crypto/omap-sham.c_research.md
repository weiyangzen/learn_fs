<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-sham.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/omap-sham.c

Purpose: implements OMAP SHA/MD5 hardware hashing and HMAC acceleration for OMAP2/3/4/5, with async ahash algorithms, CPU or DMA transmit paths, runtime PM, sysfs tuning, and software fallback for small or unsupported cases.

Important APIs and functions: ahash methods include `omap_sham_init()`, `omap_sham_update()`, `omap_sham_final()`, `omap_sham_finup()`, `omap_sham_digest()`, `omap_sham_export()`, and `omap_sham_import()`. `omap_sham_prepare_request()` merges buffered bytes with new SG data, selects full blocks, holds back later bytes, and builds aligned/copied SGs. `omap_sham_xmit_cpu()` writes blocks through DIN registers while polling readiness; `omap_sham_xmit_dma()` maps SGs and starts DMA. `omap_sham_finish_req()` releases copied SGs, copies digest state, handles huge-request requeue, runtime PM, and crypto-engine completion. `omap_sham_setkey()` prepares HMAC ipad/opad or hardware auto-XOR state.

Control flow: requests buffer small data until enough bytes exist or final is called. Hardware processing is run through a crypto engine. OMAP2-style control uses `SHA_REG_CTRL`; OMAP4/5 use MODE/LENGTH and optional HMAC key processing. Interrupts and DMA callbacks both queue `done_task`, which waits until output and DMA-ready state agree.

State and persistence: `struct omap_sham_reqctx` persists partial digest, byte count, buffered data, SG walk state, operation, and flags across update/final/export/import. Transform context stores fallback shash and HMAC base shash. Global `sham.dev_list` rotates devices and global flags advertise platform features such as auto-XOR.

Dependencies and integration: crypto engine ahash APIs, DMAengine, scatterwalk, runtime PM, OF/platform resources, sysfs attributes `fallback` and `queue_len`, and software shash fallbacks.

Risks and test signals: final-block logic, huge-request requeue, HMAC auto-XOR versus software ipad/opad, and copied SG cleanup are high risk. `omap_sham_copy_sg_lists()` offset bookkeeping is subtle. Test MD5/SHA1/SHA224/SHA256/SHA384/SHA512 and HMAC vectors, update/final streaming, import/export, zero/small buffers, fallback threshold changes, DMA-disabled polling, OMAP2 big-endian SHA1, OMAP4/5 register layouts, and runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/omap-sham.c -->
