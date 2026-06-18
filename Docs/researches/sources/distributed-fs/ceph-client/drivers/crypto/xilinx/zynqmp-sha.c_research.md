
# sources/distributed-fs/ceph-client/drivers/crypto/xilinx/zynqmp-sha.c

Purpose: ZynqMP SHA3-384 hardware acceleration driver. It registers a `sha3-384` shash implementation backed by firmware for one-shot digest and by software fallback for init/update/finup streaming operations.

Important APIs, types, and functions: `struct zynqmp_sha_drv_ctx` owns the shash algorithm and device pointer. `struct zynqmp_sha_tfm_ctx` stores device and fallback shash. `zynqmp_sha_init_tfm()` allocates fallback. `zynqmp_sha_init()`, `zynqmp_sha_update()`, and `zynqmp_sha_finup()` import/export fallback state. `__zynqmp_sha_digest()` calls `zynqmp_pm_sha_hash()` INIT/UPDATE/FINAL using coherent update/final buffers. `zynqmp_sha_digest()` serializes hardware digest with `zynqmp_sha_lock`.

Control flow: probe verifies firmware API availability, sets 32-bit DMA mask, registers the shash algorithm, stores driver context, and allocates coherent update and final buffers. Digest initializes firmware SHA, chunks input into a 4 KiB coherent update buffer, flushes icache for each copied chunk, issues update calls, issues final into the final buffer, copies digest out, and zeroes final buffer. Remove frees coherent buffers and unregisters the shash.

State and persistence: global DMA addresses and buffers `update_dma_addr`, `final_dma_addr`, `ubuf`, and `fbuf` persist for the device lifetime. A global spinlock serializes firmware hardware use. Per-transform fallback state persists in the shash context. No disk state exists.

Dependencies and integration points: depends on firmware SHA API, DMA coherent allocation, crypto shash internals, SHA3 constants, fallback shash allocation, and platform driver matching by name `"zynqmp-sha3-384"`.

Risks and test signals: `zynqmp_sha_init_tfm()` compares `crypto_shash_descsize(hash)` with `crypto_shash_statesize(tfm_ctx->fbk_tfm)` before assigning `tfm_ctx->fbk_tfm = fallback_tfm`, so it appears to read an uninitialized pointer; this is a high-priority review/test target. Digest uses `flush_icache_range()` rather than standard DMA sync on coherent memory, which may be architecture-sensitive. Only digest is hardware accelerated; streaming paths are fallback. Test signals include `tcrypt`/crypto selftests for sha3-384 digest, init/update/final state export/import, fallback allocation failure, probe allocation unwind, concurrent digest serialization, empty input, multi-4K input, and remove cleanup.
