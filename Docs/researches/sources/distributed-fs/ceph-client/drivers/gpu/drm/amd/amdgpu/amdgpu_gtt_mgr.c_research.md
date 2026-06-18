# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gtt_mgr.c

## Purpose
`amdgpu_gtt_mgr.c` implements the TTM resource manager for AMDGPU GTT/GART address space. It tracks GART virtual address ranges with `drm_mm`, reports GTT total/used sysfs values, allocates ordinary TTM TT resources lazily or within a constrained aperture, supports standalone GART entry allocations for mappings not backed by a GTT BO, and recovers GART mappings after reset.

## Important APIs, types, and functions
The TTM callbacks are `amdgpu_gtt_mgr_new()`, `amdgpu_gtt_mgr_del()`, `amdgpu_gtt_mgr_intersects()`, `amdgpu_gtt_mgr_compatible()`, and `amdgpu_gtt_mgr_debug()` in `amdgpu_gtt_mgr_func`. Exported helpers are `amdgpu_gtt_mgr_has_gart_addr()`, `amdgpu_gtt_mgr_alloc_entries()`, `amdgpu_gtt_mgr_free_entries()`, `amdgpu_gtt_mgr_recover()`, `amdgpu_gtt_mgr_init()`, and `amdgpu_gtt_mgr_fini()`. Sysfs attributes are `mem_info_gtt_total` and `mem_info_gtt_used`.

## Control flow
Initialization sets up a TT resource manager, initializes `drm_mm` over the full GART page range, installs the manager for `TTM_PL_TT`, and marks it used. Allocation creates a `ttm_range_mgr_node`; if `place->lpfn` is nonzero it immediately reserves a GART range under `mgr->lock`, otherwise it creates a resource with `AMDGPU_BO_INVALID_OFFSET` so address allocation can be deferred. Free removes an allocated `drm_mm_node`, finalizes the TTM resource, and frees the node. Recovery walks allocated nodes and calls `amdgpu_ttm_recover_gart()` for normal BO-backed entries, skipping specially colored standalone entries.

## State and persistence behavior
State lives in `adev->mman.gtt_mgr`: a TTM manager, a `drm_mm` range allocator, and a spinlock. Standalone non-BO entries use a reserved color so recovery can skip them. Sysfs reads are live snapshots of manager size and usage. No state persists across driver reload.

## Dependencies and integration points
This file depends on DRM TTM resource-manager interfaces, `ttm_range_mgr_node`, `drm_mm`, AMDGPU memory manager state, TTM GART recovery, sysfs device attributes, and the GMC GART size. It is the GTT placement backend for BO validation/migration and non-BO physical mapping helpers.

## Risks and edge cases
Deferred resources without a GART address must be handled by callers before GPU access. Usage is checked before range insertion for non-temporary placements, so accounting and actual address exhaustion can fail separately. Standalone entries must be freed with the matching helper to avoid address leaks. `amdgpu_gtt_mgr_fini()` returns early if eviction fails, leaving cleanup incomplete by design.

## Test signals
Exercise BO allocation with and without `lpfn`, GTT exhaustion, standalone GART entry allocation/free, reset recovery, manager debug dump, sysfs total/used reporting, concurrent allocation under stress, and cleanup when resources remain busy.
