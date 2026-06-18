# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shmem.c

## Purpose
This file implements the system-memory shmem GEM backend. It allocates page-cache backed objects, builds SG tables from shmem folios, handles shrink/writeback/truncate behavior, supports pre-page-instantiation pwrite, configures cache coherency, and creates the system memory region.

## Important APIs, Types, and Functions
Important helpers are `shmem_sg_alloc_table`, `shmem_sg_free_table`, `__shmem_writeback`, `__i915_gem_object_release_shmem`, `i915_gem_object_put_pages_shmem`, `i915_gem_object_create_shmem`, `i915_gem_object_create_shmem_from_data`, `i915_gem_shmem_setup`, and `i915_gem_object_is_shmem`. Backend ops are in `i915_gem_shmem_ops`.

## Control Flow
Page acquisition creates an SG table sized by object pages, marks the mapping unevictable, allocates folios using constrained no-reclaim GFP, invokes i915 shrinker retries on failure, merges contiguous PFNs up to the DMA segment limit, trims the SG table, prepares pages for GTT DMA, falls back from large segments to PAGE_SIZE on DMA remap failure, applies bit17 swizzle, sets cache-dirty when LLC can be bypassed, and installs pages.

Release flushes or marks dirty as needed, finishes GTT mappings, saves swizzle metadata, releases folios through a batch that updates LRU/dirty/accessed state, clears dirty, and frees the SG table. `shmem_pwrite` writes directly into the shmem file only before pages are instantiated; normal pread is rejected for struct-page shmem and delegated only for phys-converted objects.

## State and Persistence Behavior
State lives in the object's shmem file, pagecache mapping, `obj->mm.madv`, dirty/cache flags, swizzle bitmap, cache coherency, domain fields, and memory-region membership. `shmem_truncate` drops all backing pages immediately and marks the object purged. `init_shmem` may create a DRM hugepage mount and names the region `system`.

## Dependencies and Integration Points
It integrates with Linux shmem/folio/writeback APIs, DRM GEM private object setup, GTT DMA mapping helpers, i915 shrinker, tiling swizzle logic, phys conversion, memory-region creation, THP mount helpers, and platform cache/LLC policy.

## Risks
Allocation is sensitive to reclaim recursion, dirty shmem behavior, and DMA segment limits. Unevictable mapping state must be cleared on every error path. Direct write short-write handling returns `-EIO`. Cache coherency differs across LLC, DGFX, and MTL one-way coherency. `shmem_truncate` leaves `mm.pages` as an error pointer, so later paths must treat purged state carefully.

## Test Signals
Signals include shmem object creation with/without THP, pwrite before and after page instantiation, shrinker/writeback/truncate behavior under memory pressure, bit17 swizzle save/restore, DMA remap fallback, cache-domain tests on LLC and non-LLC platforms, and `create_shmem_from_data` content checks.
