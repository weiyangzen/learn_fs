# subset-b-003757 TTM Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_bo_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_bo_test.c

Purpose: KUnit coverage for core `ttm_buffer_object` reservation, release, unreserve, bulk move, and pinning behavior. It uses `ttm_kunit_helpers` to construct minimal GEM-backed TTM BOs and synthetic devices without driver-specific hardware.

Important APIs and control flow: tests call `ttm_bo_reserve()`, `ttm_bo_reserve_slowpath()` indirectly through WW mutex behavior, `ttm_bo_unreserve()`, `ttm_bo_fini()`, `ttm_bo_pin()`, `ttm_bo_unpin()`, `ttm_bo_set_bulk_move()`, `ttm_resource_alloc()`, and `ttm_tt_create()`. The reservation cases cover optimistic lock acquisition, prelocked no-wait failure, ticketed `-EBUSY`, double reservation `-EALREADY`, explicit WW deadlock propagation as `-EDEADLK`, and a built-in-only interruptible wait that returns `-ERESTARTSYS`. The unreserve cases verify LRU tail movement for normal and pinned resources, and that bulk-move tracking records the last resource when a shared reservation object is released.

State and dependencies: test state is kept in KUnit allocations, temporary `ttm_device` instances, `dma_resv` locks, BO `pin_count`, `resource`, `bulk_move`, and LRU lists. It depends on KUnit, DRM GEM helper initialization, WW mutex internals, timers/kthreads for signal tests, and TTM resource helpers.

Integration points: this file validates public BO APIs against the resource manager and device LRU semantics used by drivers and execbuf paths.

Risks and test signals: tests manipulate WW mutex internals and lockdep state, so they are sensitive to reservation-lock implementation changes. They give strong regression signals for deadlock handling, delayed BO cleanup, external reservation fences, and pinning preventing LRU bulk movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_bo_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_bo_validate_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_bo_validate_test.c

Purpose: KUnit coverage for BO initialization and validation across system, VRAM-like mock managers, fallback placements, multihop moves, eviction, swapout, and empty-placement gutting. It is the broadest test file in this group and exercises production paths in `ttm_bo.c`, `ttm_bo_util.c`, `ttm_pool.c`, and mock managers.

Important APIs and control flow: helper functions build `ttm_placement`, active fences, and mock `dma_fence` objects. Test cases call `ttm_bo_init_reserved()`, `ttm_bo_validate()`, `ttm_bo_reserve()`, `ttm_bo_unreserve()`, `ttm_bo_pin()`, `ttm_resource_alloc()`, `ttm_pool_alloc()`, and test-only `ttm_bo_swapout()`. The main flows validate initial placement, revalidation with no move, desired/fallback placement selection, `-ENOMEM` mapping of failed allocation, `-EINVAL` for pinned moves, `-EMULTIHOP` bounce from VRAM through TT to system, no-placement pipeline gutting, move fence wait/no-wait behavior, swapout into shmem, normal eviction, pinned-object eviction refusal, eviction of only eligible BOs, deleted BO cleanup, busy eviction-domain failure, and recursive eviction.

State and dependencies: BO state includes `resource`, `ttm`, `page_flags`, `deleted`, `pin_count`, external or internal `dma_resv`, manager `usage`, LRU membership, and `ctx.bytes_moved`. It depends on `ttm_mock_manager`, `ttm_bad_manager`, `ttm_busy_manager`, KUnit, DRM private GEM initialization, kthreads, and fences.

Integration points: it validates how TTM clients can rely on validation to allocate resources, create/populate TT backing pages, respect fences, evict other BOs, and preserve content through multihop and swap paths.

Risks and test signals: the tests are sensitive to manager error-code conventions, fence slot behavior, and `ctx.bytes_moved` accounting. They provide strong signals for regressions in placement fallback, eviction eligibility, swap/gutting persistence, and reservation handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_bo_validate_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_device_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_device_test.c

Purpose: KUnit tests for `ttm_device_init()` and `ttm_device_fini()` device-level setup. It verifies that a TTM device is wired to DRM VMA mapping, global state, the system manager, the workqueue, and page pools.

Important APIs and control flow: `ttm_device_init_basic()` allocates a device, initializes it through `ttm_device_kunit_init()`, then checks `funcs`, `wq`, `man_drv[TTM_PL_SYSTEM]`, `sysman.use_tt`, `sysman.use_type`, manager `func`, and `dev_mapping`. `ttm_device_init_multiple()` creates three TTM devices and checks all are on the global device list. `ttm_device_fini_basic()` checks system-manager disabling, empty LRU, and removal from `man_drv`. `ttm_device_init_no_vma_man()` simulates a missing DRM VMA manager and expects `-EINVAL`. Parameterized pool tests verify that `TTM_ALLOCATION_POOL_USE_DMA_ALLOC` controls initialization of per-device DMA pool types.

State and persistence behavior: the tests observe global device-list membership, system-manager use bits, LRU emptiness, pool `dev`, `alloc_flags`, and per-cache/order pool-type fields. There is no durable persistence beyond kernel-global TTM state created and released in each case.

Dependencies and integration: depends on DRM KUnit helpers, `ttm_pool_internal.h`, and `ttm_kunit_helpers`. It tests the integration contract expected by all TTM BO, pool, VM, and swapout code: a valid `vma_manager`, workqueue, system manager, and pool.

Risks and test signals: catches invalid initialization ordering, missing VMA managers, global-list leaks, and pool flag regressions. It does not exercise teardown under live BO load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_device_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_kunit_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_kunit_helpers.c

Purpose: shared KUnit scaffolding for TTM tests. It constructs DRM devices, TTM devices, mock BOs, placements, TT objects, and device callback tables so test files can exercise TTM core code without a real GPU driver.

Important APIs and functions: exported helpers include `ttm_device_kunit_init()`, `ttm_device_kunit_init_bad_evict()`, `ttm_bo_kunit_init()`, `ttm_place_kunit_init()`, `dummy_ttm_bo_destroy()`, `ttm_test_devices_basic()`, `ttm_test_devices_all()`, `ttm_test_devices_put()`, `ttm_test_devices_init()`, `ttm_test_devices_all_init()`, and `ttm_test_devices_fini()`. `ttm_dev_funcs` supplies `ttm_tt_simple_create`, `ttm_tt_simple_destroy`, `mock_move`, `ttm_bo_eviction_valuable`, and `mock_evict_flags`; `ttm_dev_funcs_bad_evict` swaps in `bad_evict_flags`.

Control flow: `mock_move()` performs null moves when possible, requests a TT bounce for VRAM to system by returning `-EMULTIHOP`, handles system-to-TT and TT-to-system with null moves, and otherwise delegates to `ttm_bo_move_memcpy()`. `mock_evict_flags()` maps VRAM and system objects to system, TT objects to `TTM_PL_MOCK2`, and MOCK1 to no placement so eviction purges. Device helpers allocate a platform device, DRM device, optional TTM device, and clean it up via KUnit suite hooks.

State and dependencies: maintains `struct ttm_test_devices`, static placement templates, and exported callback tables. It depends on DRM KUnit helpers, GEM object init/release, TTM BO/TT/resource APIs, and KUnit-managed allocations.

Risks and test signals: because it defines the fake driver semantics, changes here can alter many tests. The multihop and eviction callbacks intentionally model edge cases that production drivers must handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_kunit_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_kunit_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_kunit_helpers.h

Purpose: header for the TTM KUnit support layer. It exposes test-only memory type constants, callback tables, device bundles, and helper constructors used across the TTM test suite.

Important APIs and types: defines `TTM_PL_MOCK1` and `TTM_PL_MOCK2` as private memory types after `TTM_PL_PRIV`. Declares `ttm_dev_funcs` and `ttm_dev_funcs_bad_evict`. Defines `struct ttm_test_devices` containing the DRM device, backing kernel `struct device`, and optional `struct ttm_device`. Declares helpers for initializing TTM devices, BOs, placements, test device bundles, and KUnit init/fini hooks.

Control flow and dependencies: this header does not implement behavior, but it defines the coupling between test cases and `ttm_kunit_helpers.c`. Consumers include BO, validation, device, resource, pool, and TT tests. It includes DRM driver, TTM device/BO/placement, DRM KUnit helper, and KUnit test headers.

State and integration points: the key state contract is that a `ttm_test_devices` instance may represent only DRM/basic device state or a fully initialized TTM device. Test suites choose `ttm_test_devices_init()` or `ttm_test_devices_all_init()` depending on whether they need a live TTM device before each test.

Risks and test signals: the private memory type values must remain outside core TTM memory type collisions. Prototype drift here breaks all KUnit files at build time, making it an immediate signal for helper API changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_kunit_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_mock_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_mock_manager.c

Purpose: KUnit-only resource managers for synthetic GPU memory domains. The main mock manager uses `gpu_buddy` to allocate address-space blocks, while bad and busy managers inject allocation failures.

Important APIs and functions: exports `ttm_mock_manager_init()`, `ttm_mock_manager_fini()`, `ttm_bad_manager_init()`, `ttm_busy_manager_init()`, and `ttm_bad_manager_fini()`. `ttm_mock_manager_alloc()` creates a `ttm_mock_resource`, initializes the embedded `ttm_resource`, translates placement flags into `GPU_BUDDY_TOPDOWN_ALLOCATION` or `GPU_BUDDY_CONTIGUOUS_ALLOCATION`, and allocates blocks from `gpu_buddy` under a mutex. `ttm_mock_manager_free()` frees buddy blocks, finalizes resource usage/LRU state, and releases memory.

Control flow: initialization allocates a manager, initializes `gpu_buddy`, sets `base->func`, `use_tt`, registers the manager in the TTM device with `ttm_set_driver_manager()`, and marks it used. Finalization evicts all resources, marks unused, destroys the buddy allocator, and unregisters the manager. Bad managers install `alloc` callbacks returning `-ENOSPC` or `-EBUSY` and a permissive `compatible` callback.

State and dependencies: state lives in `struct ttm_mock_manager` with a resource manager, buddy allocator, default page size, and lock. It depends on `gpu_buddy`, TTM resource manager APIs, and placement flags.

Risks and test signals: `ttm_mock_manager_fini()` returns early on eviction failure, which can intentionally expose cleanup issues. Error-injection managers are central to validation tests for fallback and eviction failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_mock_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_mock_manager.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_mock_manager.h

Purpose: declarations and data structures for KUnit mock TTM resource managers.

Important APIs and types: `struct ttm_mock_manager` embeds `struct ttm_resource_manager`, a `gpu_buddy` allocator, a `default_page_size`, and a mutex protecting mock BO allocations. `struct ttm_mock_resource` embeds `struct ttm_resource`, a list of allocated buddy blocks, and allocation flags. The header declares manager initialization and teardown functions for normal, bad, and busy managers.

Control flow and state: implementation consumers create managers for arbitrary test memory types, normally `TTM_PL_VRAM`, `TTM_PL_TT`, `TTM_PL_MOCK1`, or `TTM_PL_MOCK2`. Resources record buddy block lists so free paths can return exact allocations. Bad and busy managers do not use `ttm_mock_resource`; they operate through a bare `ttm_resource_manager`.

Dependencies and integration: depends on `linux/gpu_buddy.h` and TTM resource/device declarations supplied by including translation units. Integrated by validation tests and any KUnit path that needs a resource manager more realistic than the system manager.

Risks and test signals: structure layout must match the `container_of()` conversions in `ttm_mock_manager.c`. Missing or mismatched teardown declarations would leave managers registered in the device and poison later tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_mock_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_pool_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_pool_test.c

Purpose: KUnit tests for TTM page-pool allocation, reuse, DMA-address handling, freeing, and pool finalization.

Important APIs and control flow: the suite constructs `ttm_tt` objects with `ttm_tt_init()`, initializes pools with `ttm_pool_init()`, allocates with `ttm_pool_alloc()`, frees with `ttm_pool_free()`, and tears down with `ttm_pool_fini()`. Parameterized basic cases cover one-page, multi-page, above-`MAX_PAGE_ORDER`, coherent DMA, and coherent DMA above allocation limit. Tests verify page vector size, `page->private` order encoding or DMA metadata, and scatter-gather `dma_address` entries. Reuse tests prepopulate a pool, then ensure matching order/caching consumes from the expected `ttm_pool_type` LRU, while mismatch cases allocate separately and leave both pools populated after free.

State and dependencies: test state includes a basic DRM device with coherent DMA mask, KUnit-created BO/TT objects, `struct ttm_pool`, `ttm_pool_type` LRU counts, `page->private`, optional `tt->dma_address`, and `tt->num_pages`. It includes `ttm_pool_internal.h` to inspect internal pool behavior.

Integration points: tests cover the allocation layer used by `ttm_tt_populate()`, BO validation, swap restore, and shrink paths. They also validate the device flag decision made in `ttm_device_init()`.

Risks and test signals: page private metadata differs between DMA and non-DMA paths; future DMA API changes may affect assertions. The suite gives direct regression signals for high-order fallback, caching/order segregation, and whether freeing returns pages to the intended pool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_pool_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_resource_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_resource_test.c

Purpose: KUnit tests for `ttm_resource`, `ttm_resource_manager`, and the system manager allocation/free callbacks.

Important APIs and control flow: setup creates a full TTM test device and a mock BO/place. `ttm_resource_init_basic()` parameterizes system, VRAM, private memory type, and placement flags, optionally installs a test manager, and verifies resource fields, bus defaults, manager usage accounting, and LRU insertion. `ttm_resource_init_pinned()` verifies pinned resources move to the device `unevictable` list. `ttm_resource_fini_basic()` verifies LRU removal and usage decrement. Manager tests cover `ttm_resource_manager_init()`, `ttm_resource_manager_usage()`, and `ttm_resource_manager_set_used()`. System-manager tests call `man->func->alloc()` and `free()` for `TTM_PL_SYSTEM`.

State and dependencies: state includes `struct ttm_resource_test_priv`, mock resource managers, `bo->priority`, manager `usage`, LRU lists, the device `unevictable` list, placement flags, and resource bus fields. It depends on TTM resource APIs, KUnit helpers, and the system manager installed by `ttm_device_init()`.

Integration points: resource initialization is a foundational contract for BO validation, eviction, VM mappings, and pool accounting. The tests verify that resource manager accounting and LRU membership are consistent as BOs move.

Risks and test signals: assertions expose regressions in usage accounting, pinned/unevictable routing, resource bus defaults, and system manager free behavior. It does not cover full cursor or bulk-move iteration, which are mainly exercised by BO tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_resource_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_tt_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_tt_test.c

Purpose: KUnit tests for translation-table (`ttm_tt`) creation, initialization, finalization, population, unpopulation, swapout, and swapin behavior.

Important APIs and control flow: tests call `ttm_tt_init()`, `ttm_sg_tt_init()`, `ttm_tt_fini()`, `ttm_tt_create()`, `ttm_tt_destroy()`, `ttm_tt_populate()`, `ttm_tt_unpopulate()`, `ttm_tt_swapout()`, `ttm_pool_alloc()`, and `ttm_tt_swapin()`. Initialization cases check page-aligned and extra-page counts; a misaligned BO size verifies rounding up. Finalization cases verify that normal page arrays, SG DMA addresses, and shmem swap storage are released. Creation cases cover valid device BO type, invalid type `-EINVAL`, existing TT preservation, and a device callback returning NULL as `-ENOMEM`. Population cases verify NULL TT rejection, idempotent population, and unpopulation of empty and populated TT objects. Swapin verifies shmem storage is consumed and `TTM_TT_FLAG_SWAPPED` is cleared.

State and dependencies: state includes `tt->pages`, `num_pages`, `dma_address`, `swap_storage`, `page_flags`, `caching`, and BO type. It depends on full test devices, the device `ttm_tt_create` callback, shmem, and `ttm_pool`.

Integration points: TT objects back BOs in system/TT memory and are used by validation, moves, VM faults, pool backup/restore, and swapout.

Risks and test signals: catches page count rounding, stale TT replacement, population idempotence, and swap flag/storage regressions. It does not inspect all backup/restore partial-failure paths covered in `ttm_pool.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/tests/ttm_tt_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_agp_backend.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_agp_backend.c

Purpose: AGP backend implementation for TTM translation tables. It wraps `struct ttm_tt` with AGP allocation/bind state so drivers using AGP aperture memory can bind TT pages into an AGP bridge.

Important APIs and functions: exports `ttm_agp_bind()`, `ttm_agp_unbind()`, `ttm_agp_is_bound()`, `ttm_agp_destroy()`, and `ttm_agp_tt_create()`. `ttm_agp_tt_create()` allocates `struct ttm_agp_backend`, stores the bridge, initializes the embedded TT with write-combined caching, and returns the TT pointer. `ttm_agp_bind()` allocates AGP memory, fills it with TT pages or the global dummy read page for holes, sets cached or uncached AGP type, and binds at `bo_mem->start`. `ttm_agp_unbind()` unbinds if bound or frees AGP memory if only allocated. Destroy unbinds, finalizes TT, and frees the wrapper.

State and persistence: persistent runtime state is `agp_be->mem`, `agp_be->bridge`, TT page vector, caching mode, and global dummy page from `ttm_glob`. There is no durable storage.

Dependencies and integration: depends on Linux AGP backend APIs, `ttm_tt`, `ttm_resource`, and TTM global initialization. It integrates as a driver-provided TT create/bind backend for legacy AGP-capable DRM drivers.

Risks and test signals: binding uses dummy pages for missing TT entries and assumes `ttm_glob.dummy_read_page` exists. Error handling logs AGP bind failure but leaves `agp_be->mem` assigned. No local KUnit coverage in this subset directly exercises AGP behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_agp_backend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_backup.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_backup.c

Purpose: shmem-backed page backup service used by TTM pool shrinking and TT backup/restore. It converts page indices to nonzero handles, writes page contents into shmem, copies them back, drops backed-up ranges, and reports available swap-backed capacity.

Important APIs and functions: `ttm_backup_shmem_create()` creates a shmem file. `ttm_backup_backup_page()` reads or creates a shmem folio at an index, marks it accessed/dirty, copies the source page, optionally starts writeback with `shmem_writeout()`, and returns a handle. `ttm_backup_copy_page()` reads a folio by handle and copies it into a destination page. `ttm_backup_drop()` truncates the page range for a handle. `ttm_backup_fini()` drops the file reference. `ttm_backup_bytes_avail()` exports approximate backup space based on swap pages.

State and persistence: data persists in an anonymous shmem file until dropped or `fput()`. Handles are `idx + 1` so zero can represent no content or error-like state. Dirty/writeback state is managed at folio level.

Dependencies and integration: used by `ttm_pool_backup()`, `ttm_pool_restore_and_alloc()`, and shrinking paths. It depends on shmem, folios, swap accounting, and page copy helpers.

Risks and test signals: reclaim-context callers must respect `__GFP_FS` and `__GFP_IO` constraints documented in comments. `ttm_backup_bytes_avail()` is approximate, so backup attempts can still fail. Local test coverage is indirect through TT swap and BO swapout tests, while partial backup/restore failures rely on pool fault-injection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo.c

Purpose: core TTM buffer-object lifecycle, placement validation, eviction, resource allocation, swapout, pinning, LRU interaction, and initialization code.

Important APIs and functions: exports `ttm_bo_move_to_lru_tail()`, `ttm_bo_set_bulk_move()`, `ttm_bo_fini()`, `ttm_bo_eviction_valuable()`, `ttm_bo_pin()`, `ttm_bo_unpin()`, `ttm_bo_mem_space()`, `ttm_bo_validate()`, `ttm_bo_init_reserved()`, `ttm_bo_init_validate()`, `ttm_bo_unmap_virtual()`, `ttm_bo_wait_ctx()`, `ttm_bo_populate()`, `ttm_bo_setup_export()`, and test-only `ttm_bo_swapout()`.

Control flow: validation first handles empty placement by pipeline gutting, checks compatibility, rejects pinned moves, allocates resources with an initial non-forcing pass then an eviction pass, and handles driver-requested `-EMULTIHOP` by bouncing through a temporary placement. Moves create/populate TT backing when needed, unmap VM mappings, reserve fences, call the driver move callback, and account bytes moved. Eviction walks resource-manager LRUs, reserves BOs, skips pins or nonvaluable BOs, handles deleted BO cleanup, and retries allocation after progress. Release individualizes external reservations, removes VMA offsets, frees IO mappings, and either destroys immediately or resurrects the BO for delayed work if fences, init-on-free, SG type, or locking prevent immediate cleanup. Swapout moves BOs to system if needed, waits idle, notifies drivers, backs TT pages to shmem, and updates LRU state.

State and dependencies: key state includes BO kref, `deleted`, `pin_count`, `bulk_move`, `resource`, `ttm`, `base.resv`, VMA node, manager LRU/usage, eviction fences, `ctx.bytes_moved`, and global BO count. It depends on TTM resource, TT, pool, VM unmap, DMA-resv, DRM VMA, dmem cgroup limits, and driver callbacks.

Risks and test signals: high-risk areas are reservation ordering, delayed deletion, multihop ownership of `res`, eviction fence slots, ENOSPC-to-ENOMEM compatibility, and LRU cursor stability. KUnit validation and BO tests cover many regressions, but real driver move callbacks remain integration-sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_internal.h

Purpose: small private header for internal BO reference helpers used inside TTM implementation files.

Important APIs: defines inline `ttm_bo_get()` as `kref_get(&bo->kref)`, inline `ttm_bo_get_unless_zero()` as guarded `kref_get_unless_zero()`, and declares `ttm_bo_put()`.

Control flow and state: these helpers protect `struct ttm_buffer_object` lifetime during LRU walks, lookups, and asynchronous cleanup. `ttm_bo_get_unless_zero()` is specifically used where objects can be concurrently removed or destroyed, such as LRU eviction traversal and DMA mapping clearing.

Dependencies and integration: includes public `drm/ttm/ttm_bo.h` and is consumed by core files such as `ttm_bo.c` and `ttm_device.c`. The actual release path is implemented in `ttm_bo.c` through `kref_put(..., ttm_bo_release)`.

Risks and test signals: because these are lifetime primitives, misuse can cause use-after-free or leaked BOs. Tests that walk LRUs, delayed-delete BOs, or clear DMA mappings indirectly depend on this contract. The header intentionally exposes minimal API surface, reducing drift risk but making its semantics central to concurrency correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_util.c

Purpose: utility layer for BO memory IO reservation, CPU mappings, memcpy and accelerated move cleanup, ghost BOs, pipeline gutting, LRU walks, and shrink helpers.

Important APIs and functions: exports `ttm_mem_io_reserve()`, `ttm_mem_io_free()`, `ttm_move_memcpy()`, `ttm_bo_move_memcpy()`, `ttm_io_prot()`, `ttm_bo_kmap_try_from_panic()`, `ttm_bo_kmap()`, `ttm_bo_kunmap()`, `ttm_bo_vmap()`, `ttm_bo_vunmap()`, `ttm_bo_move_accel_cleanup()`, `ttm_bo_move_sync_cleanup()`, `ttm_lru_walk_for_evict()`, `ttm_bo_lru_cursor_*()`, `ttm_bo_shrink()`, `ttm_bo_shrink_suitable()`, and `ttm_bo_shrink_avoid_wait()`.

Control flow: memcpy moves initialize TT or linear IO iterators for source and destination, populate swapped TT when needed, optionally clear instead of copying nonexistent data, then synchronously clean up old resources. Accelerated moves attach a fence and either move old memory to a ghost BO, remember a pipelined eviction fence, or wait and free. Pipeline gutting purges content, creating an unpopulated clearing TT or ghosting old contents if fences are active. LRU cursors combine resource-cursor iteration, trylock/ticket-lock reservation, ref acquisition, and validation that the BO still owns the same memory type.

State and dependencies: manages resource bus mappings, kmap/vmap/ioremap state, ghost BO krefs, DMA fences, TT population, bulk move, LRU cursor state, and backup/shrink flags. It depends on TTM resource/kmap iterators, DMA-resv, DRM cache helpers, VM mapping APIs, and `ttm_tt_backup()`.

Risks and test signals: TODOs note direct member copy in ghost BOs and eviction fence slot limits. High-risk areas are IO map cleanup symmetry, encrypted/decrypted page protections, ghost ownership of TT/resource, and LRU walk lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_vm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_vm.c

Purpose: VM fault, mmap, and CPU access helpers for memory mapped TTM BOs. It maps either IO memory PFNs or TT backing pages into user VMAs while avoiding reservation/mmap lock inversions.

Important APIs and functions: exports `ttm_bo_vm_reserve()`, `ttm_bo_vm_fault_reserved()`, `ttm_bo_vm_dummy_page()`, `ttm_bo_vm_fault()`, `ttm_bo_vm_open()`, `ttm_bo_vm_close()`, `ttm_bo_access()`, `ttm_bo_vm_access()`, and `ttm_bo_mmap_obj()`. Internal helpers handle idle waits and PFN calculation.

Control flow: `ttm_bo_vm_fault()` reserves the BO with retry-aware logic, enters the DRM device, faults real pages through `ttm_bo_vm_fault_reserved()`, or maps a dummy zero page if the DRM device is unplugged. The reserved fault path waits for pipelined moves, reserves IO memory, computes VMA-relative BO page offset, applies caching protection, populates TT pages for non-IO resources, decrypts IO mappings, and prefaults up to `TTM_BO_VM_NUM_PREFAULT` pages with `vmf_insert_pfn_prot()`. `ttm_bo_vm_reserve()` drops `mmap_lock` when fault retry allows it and rejects non-mappable external TT pages. Access helpers reserve the BO and either kmap system/TT memory or call a driver `access_memory` hook.

State and dependencies: uses VMA `vm_private_data`, GEM references, `bo->resource->bus`, `bo->ttm`, reservation fences, VMA node offsets, and device unplug state. It depends on DRM managed actions, GEM object refcounting, VM flags, and TTM mapping helpers.

Risks and test signals: lock ordering around mmap fault retry is critical. Dummy-page lifetime is tied to `drmm_add_action_or_reset()`. Imported non-mappable pages return SIGBUS. This subset has no direct VM KUnit file, so regressions are mostly integration-tested by drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_device.c

Purpose: global and per-device TTM initialization, teardown, swapout orchestration, hibernation preparation, and DMA mapping clearing.

Important APIs and functions: exports `ttm_glob`, `ttm_device_prepare_hibernation()`, `ttm_global_swapout()`, `ttm_device_swapout()`, `ttm_device_init()`, `ttm_device_fini()`, and `ttm_device_clear_dma_mappings()`. Internal `ttm_global_init()` and `ttm_global_release()` reference-count global state.

Control flow: global init creates the `ttm` debugfs root, sizes pool and TT managers to about half system memory with a DMA32 cap, initializes pool/TT managers, allocates a zeroed dummy read page, initializes the global device list and BO count, and creates debugfs stats. Device init rejects missing VMA manager, initializes global state, allocates a high-priority reclaim workqueue, stores driver funcs and allocation flags, initializes the system manager and pool, sets LRU locks/lists/mapping, and links the device into the global list. Teardown removes from the global list, drains/destroys the workqueue, disables/unregisters the system manager, finalizes the pool, and releases globals. Swapout walks devices or managers with `use_tt`, invoking `ttm_bo_swapout()`.

State and dependencies: state includes `ttm_glob_use_count`, `ttm_glob`, `ttm_debugfs_root`, per-device workqueue, managers, pool, `unevictable`, global `device_list`, and `dummy_read_page`. It depends on debugfs, sysinfo, TTM pool/TT managers, TTM BO swapout, and resource managers.

Risks and test signals: global refcounting and device-list locking are central. A visible bug-like risk is teardown debug logging checking `man->lru[0]` inside a loop over priorities. KUnit device tests cover initialization, pool flags, missing VMA manager, and basic teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_execbuf_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_execbuf_util.c

Purpose: execbuf helper utilities for reserving multiple BOs with WW mutex deadlock handling, backing off reservations, and attaching a completion fence to all reserved BOs.

Important APIs and functions: exports `ttm_eu_backoff_reservation()`, `ttm_eu_reserve_buffers()`, and `ttm_eu_fence_buffer_objects()`. The private `ttm_eu_backoff_reservation_reverse()` unlocks already-reserved BOs in reverse order after a failed reservation attempt.

Control flow: `ttm_eu_reserve_buffers()` optionally initializes a WW acquire context, iterates `struct ttm_validate_buffer` entries, calls `ttm_bo_reserve()`, handles duplicate reservation `-EALREADY` by moving entries to a duplicate list, reserves the requested number of fences, and on failure backs off prior reservations. If failure was `-EDEADLK`, it uses `ttm_bo_reserve_slowpath()`, reserves fences for that BO, moves the entry to the front, and restarts iteration. `ttm_eu_backoff_reservation()` moves each BO to the LRU tail and unlocks it, then finalizes the ticket. `ttm_eu_fence_buffer_objects()` adds the supplied fence as read or write based on `num_shared`, moves BOs to LRU tail, unlocks, and finalizes the ticket.

State and dependencies: works on caller-owned validation lists, optional duplicate lists, BO reservation locks, reserved fence slots, WW acquire contexts, and LRU position. It depends on TTM BO reservation APIs and DMA-resv fence semantics.

Integration points: used by DRM drivers around command submission validation. Risks include incorrect duplicate handling, reservation leaks on error, and wrong fence usage classification. No direct KUnit file in this subset targets execbuf helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_execbuf_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_module.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_module.c

Purpose: module-level TTM description and architecture-specific caching-to-page-protection helper.

Important API: `ttm_prot_from_caching(enum ttm_caching caching, pgprot_t tmp)` maps TTM caching modes to architecture page protections. Cached mappings are unchanged. Write-combined mappings use `pgprot_writecombine()` where supported. Uncached mappings use `pgprot_noncached()` on supported architectures, with x86 handling excluding UML and checking CPU generation.

Control flow and state: the function is stateless and purely transforms a `pgprot_t`. Module metadata declares authors, description, and license. A documentation block briefly describes TTM as a memory manager for accelerator devices with dedicated memory, with a TODO for deeper design background.

Dependencies and integration: includes Linux module/device/page-table/scheduler/debugfs headers, DRM sysfs, and TTM caching definitions. The helper is declared through TTM headers and used by `ttm_io_prot()` and VM mapping paths to ensure CPU mappings match BO or resource caching.

Risks and test signals: correctness is architecture-sensitive. Wrong protection selection can cause cache incoherency, data corruption, or poor performance when mapping TT pages or IO memory. There is no direct unit test in this subset; coverage is mostly through driver mmap/kmap behavior and architecture build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_module.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_module.h

Purpose: private TTM module header for shared internal declarations.

Important APIs and declarations: defines `TTM_PFX` as the debug/logging prefix, forward declares `struct dentry` and `struct ttm_device`, declares external `ttm_debugfs_root`, and declares `ttm_sys_man_init(struct ttm_device *bdev)`.

Control flow and state: no executable behavior exists here. It provides shared linkage for files that need the global debugfs root or system manager initializer. `ttm_debugfs_root` is created and destroyed in `ttm_device.c`; `ttm_sys_man_init()` is implemented outside this subset in the system manager file but is called by `ttm_device_init()`.

Dependencies and integration: included by core TTM implementation files such as device, pool, BO, and module code. It keeps private declarations out of public DRM TTM headers.

Risks and test signals: declaration drift would be caught at build time. The main integration risk is global debugfs root lifetime: files using it assume global initialization has happened through `ttm_device_init()` before debugfs entries are created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_pool.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_pool.c

Purpose: TTM page-pool implementation for TT backing pages, DMA mappings, cache-attribute pooling, backup/restore, shrinker integration, debugfs, and global pool manager lifecycle.

Important APIs and functions: exports `ttm_pool_alloc()`, `ttm_pool_free()`, `ttm_pool_init()`, `ttm_pool_fini()`, and `ttm_pool_debugfs()`. It also implements `ttm_pool_restore_and_alloc()`, `ttm_pool_drop_backed_up()`, `ttm_pool_backup()`, `ttm_pool_mgr_init()`, and `ttm_pool_mgr_fini()`. Internal helpers allocate/free DMA or normal pages, map/unmap DMA addresses, apply x86 caching transitions, manage `ttm_pool_type` LRUs, shrink pooled pages, split high-order pages for swap, and resume partial restores.

Control flow: allocation chooses the largest feasible order, first tries a matching pool type, falls back to system allocation, stages caching transitions, maps DMA addresses, and commits pages into the TT. Restore allocation tracks `ttm_pool_tt_restore` snapshots so interrupted shmem copy-in can resume. Free walks page ranges, drops backup handles or returns pages to pools, then shrinks pools above per-node limits. Backup rejects already backed-up TT, low swap capacity, or DMA-alloc pools, optionally purges pages, otherwise writes pages to shmem handles and frees pages. Global manager init creates per-cache/order global pools, debugfs files, optional fault-injection hooks, and a NUMA-aware shrinker.

State and dependencies: state includes per-pool `dev`, `nid`, `alloc_flags`, cache/order pool types, global pool arrays, per-node limits and allocated counts, `shrinker_list`, `pool_shrink_rwsem`, TT page and DMA arrays, backup handles, and restore snapshots. It depends on DMA API, list_lru, shrinker, debugfs, shmem backup, page cache attribute APIs, NUMA, and TTM TT/BO.

Risks and test signals: comments flag illegal DMA API abuse in converting coherent vaddr to page. High-risk areas include cache restoration, DMA unmap symmetry, partial backup failure, high-order splitting, reclaim locking, and pool-type lifetime versus concurrent shrinkers. KUnit pool tests cover allocation/free basics but not all backup fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_pool_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_pool_internal.h

Purpose: internal inline helpers for interpreting `struct ttm_pool` allocation flags.

Important APIs: `ttm_pool_uses_dma_alloc()` checks `TTM_ALLOCATION_POOL_USE_DMA_ALLOC`, `ttm_pool_uses_dma32()` checks `TTM_ALLOCATION_POOL_USE_DMA32`, and `ttm_pool_beneficial_order()` returns the low byte of `alloc_flags` as the largest order that is considered beneficial for direct reclaim.

Control flow and state: the helpers are pure flag readers. They are used by pool allocation, freeing, initialization, tests, and device pool assertions to select DMA versus global pools, set `GFP_DMA32`, decide when to suppress direct reclaim for high-order allocations, and expose expected pool behavior to KUnit.

Dependencies and integration: includes TTM allocation and pool public headers. It is intentionally private to TTM implementation and tests, avoiding exposure of allocation flag interpretation as public ABI.

Risks and test signals: any change in flag layout, especially the low-byte beneficial-order encoding, must be coordinated with callers in `ttm_pool.c` and tests in `ttm_pool_test.c`/`ttm_device_test.c`. Because the helpers are simple, build and KUnit assertion failures are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_pool_internal.h -->
