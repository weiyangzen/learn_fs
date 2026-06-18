<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.c

## Purpose
Builds and manages refcounted scatter-gather tables for i915 memory ranges represented by DRM MM nodes or TTM buddy allocations.

## Important APIs, types, and functions
- `i915_sg_trim()` shrinks an sg table from `orig_nents` to the effective `nents`.
- `i915_refct_sgt_init()` initializes `struct i915_refct_sgt` with default release ops.
- `i915_rsgt_from_mm_node()` creates a refcounted sg table from a contiguous `drm_mm_node`.
- `i915_rsgt_from_buddy_resource()` creates a refcounted sg table from an `i915_ttm_buddy_resource` block list.

## Control flow
Both constructors allocate an `i915_refct_sgt`, initialize size/refcount/release ops, allocate a worst-case sg table, then fill entries by walking the source range or buddy blocks. Adjacent physical/device ranges are coalesced when offsets are contiguous and the current segment is below the maximum aligned segment size. Final tables are marked with `sg_mark_end()` and trimmed.

## State and persistence
The produced `i915_refct_sgt` persists until its kref reaches zero, then the default release frees the sg table and wrapper. DMA address/length fields encode GPU memory offsets plus `region_start`, not CPU-mapped page ownership.

## Dependencies and integration points
Depends on Linux scatterlist APIs, `drm_mm_node`, `gpu_buddy`, TTM buddy resources, and i915 GEM assertions. Used by memory-region and TTM code that needs refcounted sg tables for LMEM or address-space resources.

## Risks
Segment sizing must respect `UINT_MAX`, page alignment, and sg table entry-count limits. Buddy blocks must be non-empty and sized consistently with resource size. Incorrect coalescing can create DMA segments that cross page-alignment or hardware segment limits.

## Test signals
Selftests under `selftests/scatterlist.c`, allocation failure injection, large resource tests exceeding unsigned int entry counts, mixed contiguous/noncontiguous buddy-block resources, and validation of DMA addresses and lengths against expected region offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.c -->
