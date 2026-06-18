# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_phys.c

## Purpose
This file converts eligible shmem GEM objects to physically contiguous coherent allocations and implements pread/pwrite for those physically backed objects. It supports older or special paths that require a single contiguous DMA allocation rather than normal shmem scatter-gather pages.

## Important APIs, Types, and Functions
The internal backend functions are `i915_gem_object_get_pages_phys`, `i915_gem_object_put_pages_phys`, and `i915_gem_object_shmem_to_phys`. Public helpers used by shmem and callers are `i915_gem_object_pwrite_phys`, `i915_gem_object_pread_phys`, and `i915_gem_object_attach_phys`.

## Control Flow
`i915_gem_object_attach_phys` requires a locked shmem object, rejects too-large alignment, non-shmem objects, purged objects, tiling quirks, existing mappings, and pinned pages, then unbinds active GPU use before conversion. Conversion unsets old pages, allocates a coherent DMA block rounded to a power-of-two object size, builds a one-entry SG table, copies each shmem page into the coherent allocation with cache flushes, sets the GEM pages, perma-pins them, releases the original shmem pages, and removes the object from its memory-region list.

Read and write helpers wait for GPU completion, directly copy between userspace and the coherent allocation, flush CPU cache ranges, and for writes invalidate/flush frontbuffer state.

## State and Persistence Behavior
The object changes from struct-page backed shmem to a fake single-SG physical allocation by clearing `I915_BO_FLAG_STRUCT_PAGE`. Physical pages remain permanently pinned until object release. Dirty physical data is copied back to the shmem file in `put_pages_phys` if `obj->mm.dirty` is set, then the coherent allocation is freed.

## Dependencies and Integration Points
The code integrates with shmem release helpers, frontbuffer invalidation, GT chipset flushes, tiling swizzle checks, GEM unbind/wait paths, DMA coherent allocation, shmem pagecache reads, and selftests included under `CONFIG_DRM_I915_SELFTEST`.

## Risks
The contiguous allocation can fail for large objects, and the code intentionally rejects bit17-swizzled objects. The apparent use of the SG pointer before assignment in the overflow check is fragile and depends on compiler/static-analysis behavior. Dirty copyback errors are skipped page-by-page, so data loss can occur if shmem pages cannot be reacquired. Permanent pinning reduces reclaimability.

## Test Signals
Exercise `i915_gem_object_attach_phys` selftests, pwrite/pread round trips, conversion rejection for tiled or pinned objects, GPU wait behavior before CPU access, dirty copyback after release, and memory pressure around large coherent allocations.
