<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.h

## Purpose
Declares optimized scatter-gather iterators, segment-size helpers, and the refcounted sg-table abstraction used by i915 memory managers.

## Important APIs, types, and functions
- `struct sgt_iter` and `__sgt_iter()` track page or DMA-address iteration state.
- Iteration macros include `__for_each_sgt_daddr()`, `__for_each_daddr_next()`, and `for_each_sgt_page()`.
- Segment helpers include `__sg_next()`, `i915_sg_dma_sizes()`, and `i915_sg_segment_size()`.
- `struct i915_refct_sgt_ops` and `struct i915_refct_sgt` provide kref-managed sg tables.
- Declares constructors from DRM MM nodes and TTM buddy resources.

## Control flow
Iterator macros initialize from the first sg entry, yield page or DMA addresses in fixed steps, and advance to the next sg entry when the current entry is exhausted. `__sg_next()` handles chained scatterlists without requiring the generic iterator.

## State and persistence
The header defines the persistent state carried by `i915_refct_sgt`: kref, sg table, byte size, and release ops. Iterator state is stack-local and transient.

## Dependencies and integration points
Depends on Linux scatterlist, DMA mapping, PFN helpers, Xen detection, and i915 GEM assertions. It is used throughout GEM, memory-region, page-table, and TTM code for walking pages/device addresses.

## Risks
Iterator macros rely on page-sized alignment and nonzero DMA lengths. Xen PV forces segment size to PAGE_SIZE because i915 cannot tolerate DMA bounce buffering semantics. Misusing `i915_refct_sgt_get()` on NULL is unsafe; only `put()` tolerates NULL.

## Test signals
Scatterlist selftests, Xen PV mapping tests, page-table population tests across mixed sg entries, DMA segment-size checks on devices with limited mapping sizes, and KASAN/UBSAN coverage for iterator bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_scatterlist.h -->
