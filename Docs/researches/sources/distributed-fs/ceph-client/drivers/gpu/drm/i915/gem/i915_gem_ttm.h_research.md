# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm.h

## Purpose
This header defines the i915 GEM/TTM conversion helpers, TTM placement constants, and internal TTM-backed object APIs.

## Important APIs, Types, and Functions
Inline helpers are `i915_gem_to_ttm`, `i915_ttm_is_ghost_object`, `i915_ttm_to_gem`, `i915_ttm_gtt_binds_lmem`, and `i915_ttm_cpu_maps_iomem`. It declares `i915_ttm_bo_destroy`, `__i915_gem_ttm_object_init`, `i915_ttm_sys_placement`, `i915_ttm_free_cached_io_rsgt`, `i915_ttm_resource_get_st`, `i915_ttm_adjust_lru`, `i915_ttm_purge`, and `i915_ttm_resource_mappable`. Constants map i915 memory types to TTM placements: `I915_PL_LMEM0`, `I915_PL_SYSTEM`, `I915_PL_STOLEN`, and `I915_PL_GGTT`.

## Control Flow
There is no runtime flow beyond simple inline classification. `i915_ttm_is_ghost_object` protects callbacks from downcasting non-i915 TTM ghost BOs. Resource helpers classify non-system memory as LMEM for GTT binding and IOMEM for CPU mapping.

## State and Persistence Behavior
The header stores no state but defines how callers interpret embedded TTM BOs and TTM resources. These interpretations affect cache coherency, SG table creation, mmap behavior, and migration.

## Dependencies and Integration Points
It depends on DRM TTM placement definitions and i915 GEM object types. It is used by TTM core, move, PM, local-memory region, and object lifecycle code.

## Risks
The conversion helper assumes the TTM BO is embedded in `struct drm_i915_gem_object` at `__do_not_access`; using it on ghost objects is invalid. Placement constants must match TTM memory manager registration.

## Test Signals
Build coverage, TTM callback ghost-object paths, system/LMEM resource classification tests, and migration/mmap tests validate the interface.
