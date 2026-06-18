<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_ahash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_ahash.c

Purpose: implements Rockchip SHA1, SHA256, and MD5 ahash algorithms, using hardware only for aligned one-shot digest requests and falling back for streaming or unsupported SG layout.

Important APIs and functions: `rk_ahash_need_fallback()` rejects SGs whose offsets or lengths are not 32-bit aligned. `rk_ahash_digest()` chooses fallback for bad alignment, returns fixed zero-message digests for empty input, selects a device, and queues hardware work. `rk_ahash_reg_init()` flushes hash state, clears digest registers, enables DMA interrupts, writes mode/byteswap config, and programs message length. `rk_hash_run()` resumes runtime PM, maps source SGs, selects hash mode by digest size, starts DMA for each SG, waits for completion, polls hash done status, reads digest registers little-endian, finalizes the crypto-engine request, and autosuspends the device. Init/update/final/finup/import/export methods delegate to fallback transforms.

Control flow: only `digest` takes the hardware path; all streaming methods use software fallback. Hardware processing walks SG entries sequentially, starting HRDMA for each and waiting up to 2 seconds for IRQ completion.

State and persistence: transform context stores fallback ahash. Request context stores selected device, fallback request, mode, and mapped SG count. Algorithm templates hold request/fallback statistics.

Dependencies and integration: Rockchip core device selection, runtime PM, DMA mapping, IRQ completion from `rk3288_crypto.c`, crypto engine ahash API, zero-message hash constants, and fallback ahash algorithms.

Risks and test signals: `rk_hash_unprepare()` unmaps with `sg_nents()` rather than saved mapped count, which can mismatch DMA API expectations. Completion timeout ignores interrupted wait return and relies on status. Poll condition waits for hash status register to become zero. Test SHA1/SHA256/MD5 vectors, zero messages, unaligned SG fallback, multi-SG digest, DMA error interrupt, timeout, runtime PM, and fallback streaming methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/rk3288_crypto_ahash.c -->
