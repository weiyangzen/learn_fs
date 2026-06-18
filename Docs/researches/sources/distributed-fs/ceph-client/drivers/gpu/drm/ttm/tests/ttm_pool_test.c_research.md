# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_pool_test.c

Purpose: KUnit tests for TTM page-pool allocation, reuse, DMA-address handling, freeing, and pool finalization.

Important APIs and control flow: the suite constructs `ttm_tt` objects with `ttm_tt_init()`, initializes pools with `ttm_pool_init()`, allocates with `ttm_pool_alloc()`, frees with `ttm_pool_free()`, and tears down with `ttm_pool_fini()`. Parameterized basic cases cover one-page, multi-page, above-`MAX_PAGE_ORDER`, coherent DMA, and coherent DMA above allocation limit. Tests verify page vector size, `page->private` order encoding or DMA metadata, and scatter-gather `dma_address` entries. Reuse tests prepopulate a pool, then ensure matching order/caching consumes from the expected `ttm_pool_type` LRU, while mismatch cases allocate separately and leave both pools populated after free.

State and dependencies: test state includes a basic DRM device with coherent DMA mask, KUnit-created BO/TT objects, `struct ttm_pool`, `ttm_pool_type` LRU counts, `page->private`, optional `tt->dma_address`, and `tt->num_pages`. It includes `ttm_pool_internal.h` to inspect internal pool behavior.

Integration points: tests cover the allocation layer used by `ttm_tt_populate()`, BO validation, swap restore, and shrink paths. They also validate the device flag decision made in `ttm_device_init()`.

Risks and test signals: page private metadata differs between DMA and non-DMA paths; future DMA API changes may affect assertions. The suite gives direct regression signals for high-order fallback, caching/order segregation, and whether freeing returns pages to the intended pool.
