# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object_types.h

## Purpose
Defines the central i915 GEM object data model: backend operation hooks, cache/mmap enums, mmap offset nodes, page-iterator caches, object layout, allocation and memory flags, cache coherency/domain state, tiling, page backing, migration placement, TTM/LMEM metadata, userptr/stolen/proxy unions, and conversion helpers.

## Important APIs and Types
`struct i915_lut_handle` links object handles to context VMA lookup tables. `struct drm_i915_gem_object_ops` is the backend interface for get/put/truncate/shrink pages, pread/pwrite, mmap, dma-buf export, LRU adjustment, delayed free, migration, release, and mmap ops. `enum i915_cache_level`, `enum i915_map_type`, and `enum i915_mmap_type` define cache and mapping modes. `struct i915_mmap_offset` stores fake mmap nodes. `struct i915_gem_object_page_iter` caches scatterlist lookups. `struct drm_i915_gem_object` holds the full object state.

## Control Flow and Semantics
This file is declarative but documents runtime contracts. Backend ops govern page lifecycle, shrink, migration, mmap, and release. VMA lists are ordered for GGTT/ppGTT lookup while the RB tree supports exact VMA lookup. LUT handles let object close remove context fast mappings. Cache comments define how `pat_index`, `pat_set_by_user`, `cache_coherent`, and `cache_dirty` interact, including userspace-managed PAT and non-LLC security flushing. The `mm` substructure models page pins, shrink pins, unknown state, placements, current region/resource, sg pages, page sizes, iterators, shrinker links, madvise, dirty state, and GT TLB state.

## State and Persistence Behavior
This header defines nearly all persistent GEM object state used across ioctls, mmap faults, execbuffer submissions, migration, suspend/resume, and display: flags, memory flags, PAT/coherency/dirty fields, domains, frontbuffer pointer, tiling/stride, page backing, region placement, mmap offsets, userfault tracking, PXP key instance, swizzle bit17 data, and backend-specific union state.

## Dependencies and Integration Points
Depends on Linux mmu notifier types, DRM GEM/TTM types, i915 active/selftest/VMA resource definitions, UAPI `i915_drm.h`, and GT defines. Included by core object, domain, mmap, execbuffer, LMEM, internal, frontbuffer, and other i915 files.

## Risks
The object embeds DRM GEM and TTM BO representations and must preserve aliasing/accessor assumptions. Fields are protected by different locks: reservation, `vma.lock`, `lut_lock`, `mmo.lock`, region locks, shrinker locks, RCU, and page-iterator mutexes. Cache dirty/coherency fields are security-sensitive. Backing memory flags can change with migration. `unknown_state` forbids CPU/GPU exposure after failed async move/clear.

## Test Signals
Selftest-only fields and object/migration/coherency selftests validate many invariants. IGT mmap, execbuffer, migration, userptr, PRIME, tiling, and display scanout tests exercise fields defined here. Static build checks cover layout assumptions such as `to_intel_bo(NULL) == NULL`.
