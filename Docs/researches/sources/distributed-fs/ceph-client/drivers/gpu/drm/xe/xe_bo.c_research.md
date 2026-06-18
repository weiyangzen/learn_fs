# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo.c

## Purpose
This is the main Xe buffer-object implementation. It adapts DRM GEM and TTM buffer objects to Xe memory regions, including system/TT, VRAM, stolen memory, imported dma-bufs, GGTT mappings, CPU mmap faults, shrinker reclaim, purgeable memory, pinned-kernel suspend handling, and user GEM creation ioctls.

## Important APIs, Types, and Functions
Major exported entry points include `xe_bo_init_locked`, `xe_bo_create_locked`, `xe_bo_create_user`, pinned/mapped creation helpers, `xe_bo_pin`, `xe_bo_pin_external`, `xe_bo_unpin`, `xe_bo_validate`, `xe_bo_migrate`, `xe_bo_evict`, `xe_bo_vmap`, `xe_bo_read`, `xe_gem_create_ioctl`, `xe_gem_mmap_offset_ioctl`, `xe_bo_decompress`, shrinker helpers, and pinned suspend helpers such as `xe_bo_evict_pinned` and `xe_bo_restore_pinned`. `xe_ttm_funcs` binds Xe into TTM through create/populate/unpopulate/move/evict/io-memory/access/release callbacks.

## Control Flow
Creation validates flags, size, placement, alignment, fixed ranges, VM reservation sharing, and GGTT insertion before returning a locked or unlocked BO depending on helper. Placement construction converts Xe flags to `ttm_place` arrays, choosing VRAM regions, stolen memory, TT fallback, CPU-visible VRAM constraints, contiguous requirements, and 64K/2M alignment.

TTM movement is centered on `xe_bo_move`. It handles first placement, dma-buf imports, purgeable eviction, TT/System dummy moves, multi-hop system-to-VRAM transitions through TT, GPU copy/clear via `xe_migrate`, CCS side data, and runtime PM bracketing. CPU faults first try a nonblocking fast path, then drop/retry mmap locks when needed, migrate/populate backing store, reject imported or purgeable objects, and install PTEs through TTM. GEM create ioctl validates uAPI fields, VM lookup, caching modes, scanout/visible VRAM constraints, PXP extensions, and GEM handle installation.

## State and Persistence Behavior
The file mutates `struct xe_bo` fields such as flags, placement, tile/vm association, GGTT nodes, `vmap`, pinned-list membership, purgeable state, `backup_obj`, `parent_obj`, CCS metadata, and VM/GPUVA links. It maintains shrinker accounting for populated TT pages, purgeable pages, and global GPU memory tracing. Pinned VRAM BOs can be backed up into system BOs before power loss and restored later, preserving exact placement where required. Purged BOs become terminally invalid and CPU faults/mmap reject them.

## Dependencies and Integration Points
It depends on TTM core, DRM GEM/prime/vma helpers, `dma_resv` fences, Xe validation/drm_exec, VM bind and GPUVA tracking, migrate engines, GGTT, stolen and VRAM managers, runtime PM, PXP, shrinker, SR-IOV VF CCS helpers, and tracepoints. It is called from device creation, ioctls, VM bind, display dumb-buffer creation, PM eviction, debug/test paths, and dma-buf import/export.

## Risks
The highest risks are reservation-lock ordering, asynchronous migration fences, stale VM bindings after move/purge, mismatched shrinker accounting on pin/unpin/populate/unpopulate, and losing VRAM contents across suspend if pinned lists or backup objects are mishandled. CPU mmap behavior must stay consistent with purgeable states and imported dma-bufs. Fixed placement and GGTT insertion are sensitive to tile/SR-IOV assumptions. The purge path must invalidate mappings before freeing pages or userspace/GPU could access discarded memory.

## Test Signals
Useful signals include KUnit `tests/xe_bo.c`, GEM create/mmap ioctl tests, VM bind/evict/rebind stress, dma-buf import/export migration, suspend/resume and hibernate with pinned VRAM, shrinker pressure including DONTNEED/PURGED BOs, visible-VRAM mmap faults, CCS compression/decompression paths, SR-IOV VF CCS movement, and runtime PM fault/migration races.
