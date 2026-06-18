# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_bo_validate_test.c

Purpose: KUnit coverage for BO initialization and validation across system, VRAM-like mock managers, fallback placements, multihop moves, eviction, swapout, and empty-placement gutting. It is the broadest test file in this group and exercises production paths in `ttm_bo.c`, `ttm_bo_util.c`, `ttm_pool.c`, and mock managers.

Important APIs and control flow: helper functions build `ttm_placement`, active fences, and mock `dma_fence` objects. Test cases call `ttm_bo_init_reserved()`, `ttm_bo_validate()`, `ttm_bo_reserve()`, `ttm_bo_unreserve()`, `ttm_bo_pin()`, `ttm_resource_alloc()`, `ttm_pool_alloc()`, and test-only `ttm_bo_swapout()`. The main flows validate initial placement, revalidation with no move, desired/fallback placement selection, `-ENOMEM` mapping of failed allocation, `-EINVAL` for pinned moves, `-EMULTIHOP` bounce from VRAM through TT to system, no-placement pipeline gutting, move fence wait/no-wait behavior, swapout into shmem, normal eviction, pinned-object eviction refusal, eviction of only eligible BOs, deleted BO cleanup, busy eviction-domain failure, and recursive eviction.

State and dependencies: BO state includes `resource`, `ttm`, `page_flags`, `deleted`, `pin_count`, external or internal `dma_resv`, manager `usage`, LRU membership, and `ctx.bytes_moved`. It depends on `ttm_mock_manager`, `ttm_bad_manager`, `ttm_busy_manager`, KUnit, DRM private GEM initialization, kthreads, and fences.

Integration points: it validates how TTM clients can rely on validation to allocate resources, create/populate TT backing pages, respect fences, evict other BOs, and preserve content through multihop and swap paths.

Risks and test signals: the tests are sensitive to manager error-code conventions, fence slot behavior, and `ctx.bytes_moved` accounting. They provide strong signals for regressions in placement fallback, eviction eligibility, swap/gutting persistence, and reservation handling.
