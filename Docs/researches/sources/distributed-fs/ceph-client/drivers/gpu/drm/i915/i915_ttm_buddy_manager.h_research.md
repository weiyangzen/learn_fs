<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.h

## Purpose
Declares i915's TTM buddy resource wrapper and manager APIs.

## Important APIs, types, and functions
- `struct i915_ttm_buddy_resource` extends `struct ttm_resource` with buddy block list, allocation flags, visible-page usage, and buddy allocator pointer.
- `to_ttm_buddy_resource()` upcasts from TTM resource.
- APIs initialize/finalize a manager, reserve address ranges, query visible size, query total/visible availability, and force visible size in selftests.

## Control flow
The header is mostly declarative. `to_ttm_buddy_resource()` uses `container_of()` and assumes the passed resource was allocated by this manager.

## State and persistence
The structure defines persistent per-allocation state until the TTM resource is freed. Manager state is opaque to callers.

## Dependencies and integration points
Depends on Linux list/types and TTM resource APIs. Used by TTM memory-region setup, scatterlist construction, and tests.

## Risks
Passing a resource from another TTM manager to `to_ttm_buddy_resource()` is invalid. The `used_visible_size` unit is pages, while many public API sizes are bytes or pages depending on function, so callers must respect documented units.

## Test signals
Build coverage, TTM allocation/free tests, visible availability queries, and selftest-only visible-size manipulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.h -->
