# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_pagemap.c

## Purpose

`drm_pagemap.c` implements the DRM-side wrapper around Linux `dev_pagemap` for GPU shared virtual memory. It lets DRM drivers populate an `mm_struct` range with device-private pages, migrate anonymous memory between system RAM, local device memory, and peer device memory, and evict device allocations back to RAM during CPU faults, reclaim, or device teardown. The file is meant for best-effort heterogeneous memory population where hardware unbind must reject new population and eventually return resident pages to system memory.

## Important APIs, Types, and Functions

- `struct drm_pagemap_zdd` is the per-zone-device-data wrapper stored in folio zone-device data. It holds a kref, the `drm_pagemap_devmem` allocation, and a referenced `struct drm_pagemap`.
- `drm_pagemap_migrate_to_devmem()` is the main exported migration-to-device entry. It validates an anonymous VMA, uses `migrate_vma_setup()`, asks the driver to populate destination device PFNs, copies data through driver ops, finalizes migration, and consumes the caller's devmem allocation reference.
- `drm_pagemap_evict_to_ram()` migrates an entire `drm_pagemap_devmem` allocation back to RAM without requiring the caller to hold `mmap_lock`, using `migrate_device_pfns/pages/finalize`.
- `drm_pagemap_populate_mm()` is the exported wrapper around a driver's `dpagemap->ops->populate_mm`, taking an `mm` reference and `mmap_read_lock`.
- `drm_pagemap_pagemap_ops_get()` returns `dev_pagemap_ops` with `folio_free`, `migrate_to_ram`, and `folio_split` callbacks.
- `drm_pagemap_init()`, `drm_pagemap_reinit()`, `drm_pagemap_put()`, and `drm_pagemap_destroy()` manage pagemap lifetime and cached reactivation.
- `drm_pagemap_devmem_init()` initializes allocation state: device, mm, ops, owning pagemap, size, completion, and optional pre-migration fence.
- Internal helpers such as `drm_pagemap_migrate_map_pages()`, `drm_pagemap_migrate_unmap_pages()`, `drm_pagemap_migrate_range()`, and `drm_pagemap_migrate_populate_ram_pfn()` abstract DMA mapping, peer-device mapping, batch-copy segmentation, and RAM page allocation.

## Control Flow

Migration to device starts by asserting `mmap_lock`, validating the VMA covers the requested range and is anonymous, allocating contiguous scratch arrays for source PFNs, destination PFNs, DMA addresses, and page pointers, and allocating a `drm_pagemap_zdd`. `migrate_vma_setup()` collects movable pages. The code rejects partial collection unless compound-page accounting proves the full requested range is present. It counts pages already owned by the target pagemap, optionally rejects same-pagemap fragmentation, asks the driver to populate device PFNs, then walks the range by folio order.

For each destination device page, the code initializes zone-device folio metadata and records whether the source is system RAM, local device memory, or peer device memory. `drm_pagemap_migrate_range()` flushes contiguous subranges whenever the source pagemap or ops changes. System-to-device copies call the target allocation's `copy_to_devmem`; peer/local device copies map pages through the source pagemap's `device_map` and call the source allocation's `copy_to_ram` into destination pages. After data transfer, `migrate_vma_pages()` and `migrate_vma_finalize()` install successful migrations and release unsuccessful pages.

CPU fault migration calls `drm_pagemap_migrate_to_ram()` via `dev_pagemap_ops`. It checks the allocation's `timeslice_expiration`, computes an aligned allocation-sized range clipped to the VMA, allocates RAM folios matching source folio order, maps them for DMA from device, calls `copy_to_ram`, then finalizes. Explicit eviction uses a similar path over `migrate_device_*` APIs and retries twice unless the allocation's `detached` completion indicates release already happened.

## State and Persistence

State is in memory only. `drm_pagemap_zdd` binds device pages to the devmem allocation and pagemap until folio free, at which point `drm_pagemap_folio_free()` drops the kref. `drm_pagemap_zdd_destroy()` completes `devmem->detached`, calls optional `devmem_release`, frees the wrapper, and puts the pagemap. `drm_pagemap` itself holds references to the DRM device and owning module through `struct drm_pagemap_dev_hold`; final release queues deferred work that later drops those references from process context. Device page split preserves `pgmap` and increments zdd references for the new folio.

`drm_pagemap_devmem` stores migration ops, mm, size, pre-migration fence, and a jiffies-based timeslice. On successful device migration the pre-migration fence is dropped and `timeslice_expiration` is set to delay immediate CPU-fault migration back to RAM.

## Dependencies and Integration Points

The file integrates Linux memory migration (`migrate_vma`, `migrate_device_*`), device-private page infrastructure (`dev_pagemap_ops`, `zone_device_folio_init`), DMA mapping, folios, completions, krefs, workqueues, and DRM device/module lifetime. Driver-specific behavior is supplied through `struct drm_pagemap_ops` and `struct drm_pagemap_devmem_ops` callbacks such as `populate_mm`, `populate_devmem_pfn`, `copy_to_devmem`, `copy_to_ram`, `devmem_release`, `device_map`, and `device_unmap`. It also calls utility-layer hooks from `drm_pagemap_util.c` for shrinker insertion and lockdep checks.

## Risks and Edge Cases

- `drm_pagemap_migrate_to_devmem()` consumes the devmem allocation reference on all paths; callers must not reuse it after failure.
- Partial migration, races with CPU faults, unknown device pages, VMA clipping, compound folio order, and same-pagemap fragmentation all have explicit rejection or retry paths.
- DMA mapping failures return `-EFAULT`; already mapped pages are unmapped only when the cleanup path has enough recorded state.
- The code assumes driver copy callbacks handle fences and peer/local interconnect semantics correctly.
- Fault-time migration must avoid returning pages to RAM during the protected timeslice.
- Deferred device/module release depends on `module_exit()` flushing `drm_pagemap_work`; leaked list entries trigger warnings.
- `drm_pagemap_page_to_dpagemap()` is unsafe for pages not created by this pagemap infrastructure.

## Test Signals

Useful tests include migration of anonymous pages to device memory and back, compound-page migration, same-pagemap migration allowed and denied, peer-device migration with `source_peer_migrates`, CPU fault before and after `timeslice_expiration`, explicit eviction during mm teardown, driver unbind with pending page references, DMA-map failure injection, and lockdep/KASAN/KCSAN coverage around zdd lifetime and deferred device release.
