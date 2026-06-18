# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object.c

## Purpose
Implements core i915 GEM object allocation, initialization, cache coherency setup, handle-close cleanup, delayed free/RCU lifetime, mmap/page/VMA teardown, page read helpers, migration/placement predicates, DRM GEM callbacks, and module slab setup.

## Important APIs and Functions
Important functions include `i915_gem_get_pat_index()`, `i915_gem_object_has_cache_level()`, `i915_gem_object_alloc()`, `i915_gem_object_init()`, `__i915_gem_object_fini()`, `i915_gem_object_set_cache_coherency()`, `i915_gem_object_set_pat_index()`, `i915_gem_object_can_bypass_llc()`, `i915_gem_close_object()`, `__i915_gem_object_pages_fini()`, `__i915_gem_free_object()`, `i915_gem_free_object()`, `i915_gem_flush_free_objects()`, `i915_gem_object_read_from_page()`, migration/placement helpers, and moving-fence helpers.

## Control Flow
Object init sets up VMA lists/trees, LUT and mmap locks, object ops/flags, madv state, RCU/free nodes, and page-lookup radix caches. Cache helpers translate cache levels or PAT indices into coherency flags and initial dirty state. Handle close scans object LUT entries for the closing file, revokes mmap access, deletes context fast-lookups, closes VMAs, and drops refs.

Freeing is deferred: the DRM free callback removes client accounting, queues the object on an i915 free list/workqueue after RCU readers, then worker teardown destroys VMAs, releases mmap offsets, drops pages, calls backend release, frees imports/shared reservations, and finally frees the slab object through `call_rcu()`. Migration helpers validate region, alignment, evictability, backend support, placement constraints, and then call backend `ops->migrate()`.

## State and Persistence Behavior
Owns setup and mutation of `vma`, `lut_list`, `mmo`, object flags, PAT/cache fields, page iterators, `mm.pages`, `mm.region`, placement arrays, dirty state, free-list links, and DRM GEM callbacks. Delayed free state persists in `i915->mm.free_list`, `free_count`, and `free_work`.

## Dependencies and Integration Points
Integrates with DRM GEM core, PRIME dma-buf, i915 context LUTs, VMA management, mmap helpers, TTM conversion, memory regions, PXP, frontbuffer tracking, cache flushing, client accounting, RCU/workqueues, and selftests.

## Risks
RCU/deferred-free ordering must preserve object memory for RCU lookups while teardown sleeps. Context LUT cleanup must avoid stale VMA fast-lookups after handle close. Cache/PAT behavior is security-sensitive for zeroed userspace memory and LLC bypass. Migration predicates are only strong when locked or pinned. Freeing active frontbuffers or pinned pages would violate invariants.

## Test Signals
Includes selftests for huge GEM objects, huge pages, migration, object behavior, and coherency. IGT object lifecycle, mmap, migration, PRIME, and coherency tests are relevant. Tracepoints record object destruction.
