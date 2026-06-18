# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo.c

Purpose: core TTM buffer-object lifecycle, placement validation, eviction, resource allocation, swapout, pinning, LRU interaction, and initialization code.

Important APIs and functions: exports `ttm_bo_move_to_lru_tail()`, `ttm_bo_set_bulk_move()`, `ttm_bo_fini()`, `ttm_bo_eviction_valuable()`, `ttm_bo_pin()`, `ttm_bo_unpin()`, `ttm_bo_mem_space()`, `ttm_bo_validate()`, `ttm_bo_init_reserved()`, `ttm_bo_init_validate()`, `ttm_bo_unmap_virtual()`, `ttm_bo_wait_ctx()`, `ttm_bo_populate()`, `ttm_bo_setup_export()`, and test-only `ttm_bo_swapout()`.

Control flow: validation first handles empty placement by pipeline gutting, checks compatibility, rejects pinned moves, allocates resources with an initial non-forcing pass then an eviction pass, and handles driver-requested `-EMULTIHOP` by bouncing through a temporary placement. Moves create/populate TT backing when needed, unmap VM mappings, reserve fences, call the driver move callback, and account bytes moved. Eviction walks resource-manager LRUs, reserves BOs, skips pins or nonvaluable BOs, handles deleted BO cleanup, and retries allocation after progress. Release individualizes external reservations, removes VMA offsets, frees IO mappings, and either destroys immediately or resurrects the BO for delayed work if fences, init-on-free, SG type, or locking prevent immediate cleanup. Swapout moves BOs to system if needed, waits idle, notifies drivers, backs TT pages to shmem, and updates LRU state.

State and dependencies: key state includes BO kref, `deleted`, `pin_count`, `bulk_move`, `resource`, `ttm`, `base.resv`, VMA node, manager LRU/usage, eviction fences, `ctx.bytes_moved`, and global BO count. It depends on TTM resource, TT, pool, VM unmap, DMA-resv, DRM VMA, dmem cgroup limits, and driver callbacks.

Risks and test signals: high-risk areas are reservation ordering, delayed deletion, multihop ownership of `res`, eviction fence slots, ENOSPC-to-ENOMEM compatibility, and LRU cursor stability. KUnit validation and BO tests cover many regressions, but real driver move callbacks remain integration-sensitive.
