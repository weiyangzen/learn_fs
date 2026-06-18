<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.c

## Purpose
Implements a TTM resource manager backed by the Linux GPU buddy allocator for i915 memory regions, including CPU-visible memory accounting and reserved ranges.

## Important APIs, types, and functions
- TTM manager callbacks: `i915_ttm_buddy_man_alloc()`, `i915_ttm_buddy_man_free()`, `i915_ttm_buddy_man_intersects()`, `i915_ttm_buddy_man_compatible()`, and `i915_ttm_buddy_man_debug()`.
- Public APIs: `i915_ttm_buddy_man_init()`, `i915_ttm_buddy_man_fini()`, `i915_ttm_buddy_man_reserve()`, `i915_ttm_buddy_man_visible_size()`, `i915_ttm_buddy_man_avail()`, and selftest-only `i915_ttm_buddy_man_force_visible_size()`.
- Internal manager state tracks `ttm_resource_manager`, `gpu_buddy`, reserved blocks, lock, visible size/availability/reserved pages, and default page size.

## Control flow
Allocation creates an `i915_ttm_buddy_resource`, translates TTM placement flags into buddy flags, computes minimum page size from manager default or BO alignment, checks requested range/visible availability, allocates buddy blocks, computes how many allocated pages fall in the CPU-visible aperture, updates visible availability, and returns the TTM resource. Free returns blocks to the buddy allocator, restores visible availability, finalizes the TTM resource, and frees the wrapper.

Intersection/compatibility callbacks compare a resource's blocks with a requested placement range, with fast paths for "any placement" and "CPU-visible only" checks. Init allocates the manager, initializes the buddy allocator with region size/chunk size, registers it with TTM, and marks it used. Fini marks it unused, evicts all resources, unregisters it, frees reserved blocks, verifies visible accounting, cleans up TTM, and frees the manager.

## State and persistence
Persistent manager state is registered in the TTM device per memory type. Each allocation persists as `i915_ttm_buddy_resource` with a block list, flags, used visible page count, and buddy pointer. Reserved blocks remain on the manager until fini/deallocation.

## Dependencies and integration points
Depends on Linux `gpu_buddy`, DRM buddy debug printing, TTM resource manager APIs, TTM BO placement flags, and i915 GEM assertions. Used by i915 TTM-backed memory regions and scatterlist construction.

## Risks
Visible memory accounting is critical for small-BAR systems. Range allocations must respect TTM `fpfn/lpfn`, alignment, top-down/contiguous flags, and chunk-size constraints. `i915_ttm_buddy_man_reserve()` updates visible accounting even if allocation fails after the visible range calculation, which should be checked carefully when modifying.

## Test signals
TTM memory allocation/eviction tests, small-BAR visible placement tests, contiguous and top-down allocation tests, reserved-range tests, debugfs output, selftests forcing visible size, and teardown verifying visible availability equals visible size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ttm_buddy_manager.c -->
