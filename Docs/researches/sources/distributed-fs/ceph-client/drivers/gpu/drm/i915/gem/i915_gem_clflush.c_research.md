## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_clflush.c

### Purpose

`i915_gem_clflush.c` flushes CPU cache lines for GEM objects when domain transitions require memory to become coherent with GPU access. It can perform the flush synchronously or schedule it as reservation-fence-backed work.

### Important APIs, types, and functions

The public function is `i915_gem_clflush_object()`. Internal pieces are `struct clflush`, `__do_clflush()`, `clflush_work()`, `clflush_release()`, `clflush_ops`, and `clflush_work_create()`. The work object uses `dma_fence_work` and pins object pages until release.

### Control flow

The caller must hold the object lock. The function skips flushing on discrete graphics, non-struct-page objects, or cache-coherent reads unless forced. If async operation is allowed and a reservation fence slot can be reserved, it creates clflush work, waits on prior reservation fences, adds a kernel fence, commits the work, and clears `cache_dirty`. Otherwise it flushes immediately if pages are resident. If pages are not resident, it asserts the object remains CPU-write-domain dirty for future acquire-time flush.

### State and persistence behavior

The function mutates `obj->cache_dirty`, adds kernel fences to `obj->base.resv`, pins/unpins pages for async flushing, and calls `i915_gem_object_frontbuffer_flush()` after `drm_clflush_sg()`. It does not persist data itself, but it ensures CPU cache state is written back before GPU-visible use.

### Dependencies

It depends on DRM cache helpers, i915 object/page/domain/frontbuffer helpers, `i915_sw_fence_work`, reservation fences, and tracing.

### Integration points

`i915_gem_domain.c` calls it during domain transitions, and execbuffer calls it when objects need cache cleanup before GPU execution. Frontbuffer flush integration matters for display scanout coherency.

### Risks

Incorrectly skipping flushes can expose stale CPU cache contents to GPU or display. Async flushing must pin pages and install reservation fences correctly so later GPU work waits. The DGFX path warns if `cache_dirty` appears because discrete memory is expected to follow different coherency rules.

### Test signals

Domain transition tests, execbuffer cache-dirty paths, frontbuffer update tests, async fence ordering, object eviction during async flush, and coherency tests on LLC/non-LLC systems.
