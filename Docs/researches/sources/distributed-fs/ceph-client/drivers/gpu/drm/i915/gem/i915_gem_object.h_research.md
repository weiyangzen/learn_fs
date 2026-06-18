# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_object.h

## Purpose
Main API surface for i915 GEM object users: allocation/init, lookup/refcounting, reservation locking, tiling, page pinning and lookup, kernel mapping, domain prep, cache coherency, display flush, shrinker state, waits, migration, placement, shmem helpers, and userptr hooks.

## Important APIs and Types
Exposes lookup/ref helpers, `i915_gem_object_lock()`/ww locking helpers, object flag predicates, tiling helpers, page iterator and DMA address helpers, page pin/unpin/get/put APIs, kernel map APIs, prepare read/write and finish access, cache/PAT setters, display flush helpers, migration/placement APIs, shmem sg helpers, and userptr submit/validate hooks.

## Control Flow
Most content is declarations or thin inlines. The lock inline takes the dma-resv lock with optional ww context, records locked objects in the ww list, and records contended objects on `-EDEADLK`. Pinning increments `pages_pin_count` if pages already exist or calls into page population. Unpinning asserts pages and pin count. `__start_cpu_write()` sets CPU domains and marks cache dirty when CPU writes require clflush.

## State and Persistence Behavior
Defines caller-facing mutations of object `flags`, `tiling_and_stride`, `mm.pages_pin_count`, `read_domains`, `write_domain`, `cache_dirty`, `mm.dirty`, shrinker pins, and migration/placement state. Many APIs require object reservation locking or pinned pages.

## Dependencies and Integration Points
Includes DRM GEM/file/device, memory-region, GTT, ww locking, VMA types, and object type definitions. Included by most GEM implementation files plus GT/display users.

## Risks
WW locking/ref tracking can leak references or deadlock if misused. Page offset macros prevent truncation; bypassing them is risky. Backing-type predicates require lock/pin because migration can change memory. Prepare-read/write returns with pages pinned and must be balanced by finish access.

## Test Signals
Build coverage is broad. Runtime coverage comes from object, migration, mmap, domain, userptr, and execbuffer tests. Inline assertions catch bad pin/unpin, missing pages, tiling misuse, and disabled userptr paths.
