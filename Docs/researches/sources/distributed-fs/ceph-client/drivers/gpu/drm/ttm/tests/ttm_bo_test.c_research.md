# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_bo_test.c

Purpose: KUnit coverage for core `ttm_buffer_object` reservation, release, unreserve, bulk move, and pinning behavior. It uses `ttm_kunit_helpers` to construct minimal GEM-backed TTM BOs and synthetic devices without driver-specific hardware.

Important APIs and control flow: tests call `ttm_bo_reserve()`, `ttm_bo_reserve_slowpath()` indirectly through WW mutex behavior, `ttm_bo_unreserve()`, `ttm_bo_fini()`, `ttm_bo_pin()`, `ttm_bo_unpin()`, `ttm_bo_set_bulk_move()`, `ttm_resource_alloc()`, and `ttm_tt_create()`. The reservation cases cover optimistic lock acquisition, prelocked no-wait failure, ticketed `-EBUSY`, double reservation `-EALREADY`, explicit WW deadlock propagation as `-EDEADLK`, and a built-in-only interruptible wait that returns `-ERESTARTSYS`. The unreserve cases verify LRU tail movement for normal and pinned resources, and that bulk-move tracking records the last resource when a shared reservation object is released.

State and dependencies: test state is kept in KUnit allocations, temporary `ttm_device` instances, `dma_resv` locks, BO `pin_count`, `resource`, `bulk_move`, and LRU lists. It depends on KUnit, DRM GEM helper initialization, WW mutex internals, timers/kthreads for signal tests, and TTM resource helpers.

Integration points: this file validates public BO APIs against the resource manager and device LRU semantics used by drivers and execbuf paths.

Risks and test signals: tests manipulate WW mutex internals and lockdep state, so they are sensitive to reservation-lock implementation changes. They give strong regression signals for deadlock handling, delayed BO cleanup, external reservation fences, and pinning preventing LRU bulk movement.
