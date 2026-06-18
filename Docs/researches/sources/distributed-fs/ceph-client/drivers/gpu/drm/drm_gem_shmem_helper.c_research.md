# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_shmem_helper.c

## Purpose
`drm_gem_shmem_helper.c` implements GEM objects backed by anonymous shmem pages. It is the standard helper for pageable system-memory GEM buffers, with support for page pinning, vmap/vunmap, dumb-buffer creation, mmap faults, madvise/purge, sg table creation, DMA mapping for device access, PRIME import variants, debug printing, and KUnit-only convenience wrappers.

## Important APIs, Types, And Functions
The key type is `struct drm_gem_shmem_object`, which extends GEM with `pages`, `pages_use_count`, `pages_pin_count`, `vmap_use_count`, `vaddr`, `sgt`, `madv`, purge list state, and write-combine flags. Important exports include `drm_gem_shmem_init()`, `drm_gem_shmem_create()`, `drm_gem_shmem_release()`, `drm_gem_shmem_free()`, `drm_gem_shmem_pin[_locked]()`, `drm_gem_shmem_unpin[_locked]()`, `drm_gem_shmem_put_pages_locked()`, `drm_gem_shmem_vmap_locked()`, `drm_gem_shmem_vunmap_locked()`, `drm_gem_shmem_madvise_locked()`, `drm_gem_shmem_purge_locked()`, `drm_gem_shmem_mmap()`, `drm_gem_shmem_get_sg_table()`, `drm_gem_shmem_get_pages_sgt()`, `drm_gem_shmem_prime_import_sg_table()`, and `drm_gem_shmem_prime_import_no_map()`.

## Control Flow
Initialization installs default GEM funcs, uses either regular `drm_gem_object_init()` or private object init for imported buffers, creates a fake mmap offset, initializes purge-list state, and sets a non-movable-friendly GFP mask for native shmem mappings. Page acquisition calls core `drm_gem_get_pages()`, optionally marks pages write-combined on x86, stores the page array, and sets use counts. Pinning increments the pin count or acquires pages under the reservation lock. Vmap either delegates imported objects to `dma_buf_vmap()` or pins native pages, vmaps them with write-combined protection when requested, and marks pages dirty/accessed on put. Mmap rejects COW mappings for native objects, pins pages, installs PFNMAP/DONTEXPAND/DONTDUMP flags, and uses custom fault handlers to insert PFNs. sg-table acquisition pins pages, builds an sg table, DMA maps it, caches it in `shmem->sgt`, and unwinds on failure. Purge unmaps DMA, frees the sg table, drops pages, marks `madv = -1`, removes mmap offsets, truncates shmem, and invalidates mapping pages.

## State And Persistence Behavior
The helper tracks separate page use, pin, and vmap reference counts. Native page arrays and cached sg tables persist until unpinned, purged, or object release. Imported objects preserve exporter-owned state through `import_attach`, external `resv`, and optionally an unmapped dma-buf attachment when `prime_import_no_map` is used. `madv` acts as purgeability state: non-negative means retained, negative means purged. VMAs hold GEM references via core vm open/close while shmem VM open/close adjusts page use counts.

## Dependencies And Integration Points
This file integrates with shmem-backed core GEM pages, dma-resv locking, dma-buf PRIME, Linux vm fault insertion including optional PMD PFNMAP huge faults, x86 page cacheability helpers, DMA sg mapping, DRM dumb-buffer sizing, and KUnit visibility. Drivers consume it through `drm_gem_object_funcs`, driver PRIME callbacks, dumb-create callbacks, and shrinker/purge code.

## Risks
Reference-count symmetry is the main risk: page use, pin, vmap, mmap, and sg-table lifetimes overlap. Purge is only valid for purgeable objects and must not race active mappings or DMA use. Imported objects bypass native page pinning and must keep dma-buf attachment/reservation ownership correct. Fault insertion must reject purged objects and out-of-range offsets. Write-combined page attribute changes are x86-specific and must be reverted before pages are returned. The KUnit helper `drm_gem_shmem_vunmap()` ignores the return from `dma_resv_lock_interruptible()`, which is acceptable for test-only visibility but should not be copied into production paths.

## Test Signals
Coverage should include shmem dumb create, mmap faults and write faults, forked VMA open/close accounting, vmap/vunmap reference counts, sg-table caching and DMA unmap on release, madvise/purge behavior under shrinker pressure, imported dma-buf mapping and no-map import, x86 write-combine attribute transitions, PMD fault fallback, and KUnit tests for vmap, madvise, and purge helpers.
