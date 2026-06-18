# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mem_pool.c

## Purpose
`xe_mem_pool.c` implements a DRM MM suballocation pool backed by one pinned, CPU-mapped Xe BO, with optional shadow BO support for staged/atomic updates.

## Important APIs, Types, And Functions
- `struct xe_mem_pool` contains a `drm_mm`, active BO, optional shadow BO, swap mutex, CPU pointer, and iomem flag.
- `xe_mem_pool_init()` creates the backing BO, optional CPU shadow memory for iomem mappings, optional shadow BO, initializes `drm_mm`, and registers managed teardown.
- Shadow helpers: `xe_mem_pool_sync()`, `xe_mem_pool_swap_shadow_locked()`, and `xe_mem_pool_sync_shadow_locked()`.
- Address/data helpers: `xe_mem_pool_gpu_addr()`, `xe_mem_pool_cpu_addr()`, `xe_mem_pool_bo_flush_write()`, `xe_mem_pool_bo_sync_read()`, and `xe_mem_pool_node_cpu_addr()`.
- Node lifecycle: `xe_mem_pool_alloc_node()`, `xe_mem_pool_insert_node()`, and `xe_mem_pool_free_node()`.
- `xe_mem_pool_dump()` dumps allocator state.

## Control Flow
Initialization allocates a managed BO of `size`, reserves `guard` bytes at the end by giving `drm_mm` only `size - guard`, and optionally creates a shadow BO protected by `swap_guard`. Clients allocate nodes, write through CPU addresses, flush/sync for iomem-backed BOs, and free nodes when done. Shadow users must hold the swap guard while syncing or swapping.

## State And Persistence
The pool persists until DRM-managed cleanup. The active BO and optional shadow BO are pinned and mapped. For iomem BO mappings, `pool->cpu_addr` points to separate kernel memory and explicit flush/readback copies synchronize with the BO. `drm_mm` state tracks active suballocations.

## Dependencies And Integration Points
Depends on Xe BO creation/mapping, tile/device helpers, `xe_map`, DRM MM, managed DRM cleanup, and MI command headers. It is intended for Xe subsystems needing persistent GPU-addressable suballocations.

## Risks
`xe_mem_pool_insert_node()` uses raw `drm_mm_insert_node()` without internal locking, so callers must serialize allocations if needed. Shadow swap changes `pool->bo`, so clients caching GPU addresses must refresh after swaps. For iomem mappings, forgetting flush/sync leaves CPU and GPU views stale. `xe_mem_pool_free_node()` assumes the node was inserted before remove.

## Test Signals
Test pool size/guard handling, allocation/free fragmentation, iomem flush/readback, shadow initialization/sync/swap under lockdep, GPU address changes after swap, and dump output for allocator state.
