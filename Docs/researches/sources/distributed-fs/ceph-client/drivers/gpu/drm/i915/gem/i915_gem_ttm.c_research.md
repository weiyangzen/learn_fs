# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm.c

## Purpose
This file is the i915 GEM integration layer for TTM-backed objects. It implements TTM page-vector creation/population, placement selection, eviction policy, resource-to-SG conversion, shrink/purge behavior, mmap fault handling, object lifecycle, and the TTM system memory region.

## Important APIs, Types, and Functions
Important APIs include `i915_ttm_sys_placement`, `i915_ttm_free_cached_io_rsgt`, `i915_ttm_purge`, `i915_ttm_resource_get_st`, `i915_ttm_resource_mappable`, `i915_ttm_driver`, `i915_ttm_adjust_lru`, `__i915_gem_ttm_object_init`, and `i915_gem_ttm_system_setup`. `struct i915_ttm_tt` extends `ttm_tt` with DMA device, cached refcounted SG table, shmem mode, and optional shmem file. Object ops are `i915_gem_ttm_obj_ops`; TTM callbacks are in `i915_ttm_bo_driver`.

## Control Flow
Placement construction maps GEM memory regions to TTM memory types, applies fixed offsets, contiguous flags, mappable IO limits, GPU-only top-down placement, and fallback placements. `i915_ttm_get_pages` validates initial desired placement without eviction, retries full placement with eviction, populates TT pages if needed, converts current resource into a cached SG table, installs GEM pages, and adjusts TTM LRU priority.

TT population either uses shmem-backed external pages for shrinkable cached objects or the TTM pool for ordinary TT pages. Purge validates into an empty placement, truncates shmem files, clears domains, drops cached IO SG state, and marks the object purged. Mmap faults reserve the BO, reject purged or read-only writes, resurrect swapped-out system TT resources, migrate non-mappable LMEM to a CPU-visible placement if possible, then delegate to TTM VM fault handling while holding runtime PM for IOMEM faults.

## State and Persistence Behavior
This file coordinates `obj->__do_not_access` as an embedded `ttm_buffer_object`, `obj->mm.region`, placements, `bo_offset`, `obj->mm.rsgt`, cached IO SG tables, `obj->ttm.get_io_page`, `obj->mm.ttm_shrinkable`, object domains, cache coherency, userfault lists, TTM resources, TT shmem files, and purged/swapped flags. TTM-backed objects self-manage shrink-list membership outside the normal `mm.pages` lifecycle.

## Dependencies and Integration Points
It integrates with DRM TTM core, i915 TTM buddy managers, memory regions, shmem SG allocation, GEM page helpers, TTM move and PM modules, mmap APIs, runtime PM userfault tracking, local-memory IOMEM mappings, DMA mapping, and refcounted SG helpers.

## Risks
TTM ghost objects must not be downcast. Region state can diverge from TTM resource state during eviction and is corrected only for allowable placements. Cached SG tables and radix iterators must be invalidated on moves. Non-mappable small-BAR LMEM faults can fail with SIGBUS. Shrinker and TTM LRUs interact through extra shrink pins. Purged objects use NULL resources and special recovery paths.

## Test Signals
TTM object create/destroy tests, placement fallback and eviction tests, LMEM/system migration, small-BAR mmap faults, shrink/purge/writeback, swapped TT recovery, cached SG lifetime, userfault RPM tracking, ghost object callback coverage, and suspend/resume with TTM objects are essential signals.
