# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_tt_test.c

Purpose: KUnit tests for translation-table (`ttm_tt`) creation, initialization, finalization, population, unpopulation, swapout, and swapin behavior.

Important APIs and control flow: tests call `ttm_tt_init()`, `ttm_sg_tt_init()`, `ttm_tt_fini()`, `ttm_tt_create()`, `ttm_tt_destroy()`, `ttm_tt_populate()`, `ttm_tt_unpopulate()`, `ttm_tt_swapout()`, `ttm_pool_alloc()`, and `ttm_tt_swapin()`. Initialization cases check page-aligned and extra-page counts; a misaligned BO size verifies rounding up. Finalization cases verify that normal page arrays, SG DMA addresses, and shmem swap storage are released. Creation cases cover valid device BO type, invalid type `-EINVAL`, existing TT preservation, and a device callback returning NULL as `-ENOMEM`. Population cases verify NULL TT rejection, idempotent population, and unpopulation of empty and populated TT objects. Swapin verifies shmem storage is consumed and `TTM_TT_FLAG_SWAPPED` is cleared.

State and dependencies: state includes `tt->pages`, `num_pages`, `dma_address`, `swap_storage`, `page_flags`, `caching`, and BO type. It depends on full test devices, the device `ttm_tt_create` callback, shmem, and `ttm_pool`.

Integration points: TT objects back BOs in system/TT memory and are used by validation, moves, VM faults, pool backup/restore, and swapout.

Risks and test signals: catches page count rounding, stale TT replacement, population idempotence, and swap flag/storage regressions. It does not inspect all backup/restore partial-failure paths covered in `ttm_pool.c`.
