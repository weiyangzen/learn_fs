<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_tt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_tt.c

Purpose: Owns TTM translation-table page storage: creation, initialization, population/unpopulation, swap-in/swap-out, backup/restore, global page-limit accounting, shrink debugfs support, and local kmap iteration over TT pages.

Important APIs/types/functions: `ttm_tt_create()` asks the driver to allocate a `ttm_tt` and sets flags based on BO type, zero allocation, external SG objects, and encrypted guest memory. `ttm_tt_init()`, `ttm_sg_tt_init()`, and `ttm_tt_fini()` manage page/dma-address arrays and swap/backup resources. `ttm_tt_populate()` enforces `pages_limit`/`dma32_pages_limit`, invokes driver or pool allocation, and handles swapin. `ttm_tt_unpopulate()`, `ttm_tt_swapout()`, `ttm_tt_swapin()`, `ttm_tt_backup()`, `ttm_tt_restore()`, and `ttm_tt_setup_backup()` implement reclaim paths. `ttm_kmap_iter_tt_init()` maps individual pages using `kmap_local_page_prot()`.

Control flow: BO creation calls `ttm_tt_create()` under reservation lock, then driver-provided creation calls into the init helpers. Population increments global page counters for non-external TT, triggers global swapout while limits are exceeded, allocates pages through the driver or pool, sets `PRIV_POPULATED`, clears backup state, and reloads swapped data when needed. Swapout creates a shmem file, copies pages to it, unpopulates the TT, stores `swap_storage`, and marks `SWAPPED`.

State and persistence: Runtime state is in `ttm->pages`, `ttm->dma_address`, `ttm->page_flags`, `swap_storage`, `backup`, and global atomic page counters. Swap and backup use shmem/file references as temporary kernel persistence for reclaim, not durable storage.

Dependencies and integration points: Integrates TTM pool, backup helper, BO/device callbacks, shmem, Linux module params, debugfs, memory-encryption detection, DRM cache protection helpers, and KUnit/test exports. It is shared by all TTM drivers that use TT-backed BOs.

Risks and test signals: Critical risks are counter imbalance on failure, swapped/backup flag inconsistency, missing `fput()`, encrypted-memory handling, external SG page-directory layout, and copy failures during swapin/out. Test signals include page-limit pressure, driver callback failure injection, external and external-mappable BOs, DMA32 pools, swap round trips, backup restore, and kmap iterator correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_tt.c -->
