# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pages.c

## Purpose
This file is the central GEM object page-management implementation for i915. It attaches and detaches scatter-gather page tables to `drm_i915_gem_object`, pins object backing storage, manages kernel mappings, invalidates cached TLB state, supports panic-time framebuffer access, and provides fast page/DMA address lookup helpers.

## Important APIs, Types, and Functions
Key entry points are `__i915_gem_object_set_pages`, `____i915_gem_object_get_pages`, `__i915_gem_object_get_pages`, `i915_gem_object_pin_pages_unlocked`, `i915_gem_object_truncate`, `__i915_gem_object_unset_pages`, `__i915_gem_object_put_pages`, `i915_gem_object_pin_map`, `i915_gem_object_pin_map_unlocked`, `__i915_gem_object_flush_map`, `__i915_gem_object_release_map`, `__i915_gem_object_page_iter_get_sg`, `__i915_gem_object_get_page`, `__i915_gem_object_get_dirty_page`, and the DMA address helpers. `struct intel_panic` and the `i915_gem_object_panic_*` functions bridge GEM objects to `drm_panic` scanout writes.

## Control Flow
Page acquisition routes through object ops: the public pin path locks the object, calls the backend `get_pages` if no pages exist, then increments `pages_pin_count`. Setting pages initializes SG iterators, page-size masks, shrinker state, cache dirty handling, and swizzle quirks. Releasing pages refuses pinned objects, drops mmap offsets, removes the object from shrink lists, unmaps cached virtual mappings, clears lookup radix trees, invalidates per-GT TLB generation records, and calls the backend `put_pages`.

Kernel mapping flow first pins pages, selects WB/WC based on object placement and DGFX rules, waits for moving fences, and maps either struct pages via `vmap` or IOMEM PFNs via `vmap_pfn`. Reusing a mapping with a different cache type is allowed only when the caller did not enter through a preexisting pin.

## State and Persistence Behavior
The file mutates `obj->mm.pages`, `mm.mapping`, `mm.page_sizes`, page iterators, `pages_pin_count`, shrink list links, `shrink_pin`, `madv`, `dirty`, `cache_dirty`, and per-GT `mm.tlb[]`. Volatile objects temporarily become `DONTNEED` while pages are set and return to `WILLNEED` on unset. Cached kernel mappings persist until explicit release or page teardown.

## Dependencies and Integration Points
It depends on GEM object ops implemented by shmem, userptr, stolen, phys, and TTM backends; `i915_scatterlist` iterators; shrinker helpers; GTT mmap release; local-memory placement; GT TLB invalidation; display framebuffer tiling callbacks; and DRM panic scanout buffer APIs.

## Risks
Incorrect pin accounting can release active backing storage. Cache-type mismatch or missing clflush can corrupt CPU/GPU data sharing. Page-size mask errors affect GTT insertion. Radix iterator updates are concurrent and must preserve lookup correctness. Panic paths run under constrained allocation and mapping rules. IOMEM mappings require WC/PAT availability and correct physical offset calculations.

## Test Signals
Useful signals include GEM shmem/stolen/TTM selftests, pin/unpin stress, mmap and kernel-map cache mode tests, suspend/resume with TLB invalidation, dirty page read/write tests, DGFX local-memory mapping tests, panic framebuffer rendering, and shrinker pressure while objects are pinned or mapped.
