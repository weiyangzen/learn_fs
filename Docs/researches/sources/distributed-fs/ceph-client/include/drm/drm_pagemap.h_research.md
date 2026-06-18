# sources/distributed-fs/ceph-client/include/drm/drm_pagemap.h

## Purpose
`drm_pagemap.h` declares DRM's device-private pagemap interface for GPU shared virtual memory, peer-to-peer handshaking, and migration between system RAM and device memory. It wraps Linux `dev_pagemap` / `ZONE_DEVICE` pages with DRM-specific ownership, mapping, migration, and lifetime callbacks.

## Important APIs, types, and functions
Core types are `struct drm_pagemap`, `struct drm_pagemap_ops`, `struct drm_pagemap_addr`, `struct drm_pagemap_devmem`, `struct drm_pagemap_devmem_ops`, and `struct drm_pagemap_migrate_details`. `drm_pagemap_addr_encode()` packs an address, interconnect protocol, page order, and DMA direction. `drm_pagemap_ops` supplies `device_map`, `device_unmap`, `populate_mm`, and `destroy`. Public ZONE_DEVICE-gated functions include `drm_pagemap_init`, `drm_pagemap_create`, `drm_pagemap_page_to_dpagemap`, `drm_pagemap_put`, `drm_pagemap_migrate_to_devmem`, `drm_pagemap_evict_to_ram`, `drm_pagemap_populate_mm`, `drm_pagemap_destroy`, and `drm_pagemap_reinit`.

## Control flow
Drivers create or initialize a `drm_pagemap` for a `dev_pagemap`, map pages for DMA or driver-defined interconnects through `device_map`, and populate user address ranges through `populate_mm`. Migration uses device-memory allocations plus `copy_to_devmem` / `copy_to_ram`, optionally waiting on a pre-migration fence and respecting migration timeslice details. Teardown eventually calls `destroy`, which may run in atomic or reclaim context.

## State and persistence
State is runtime-only: kref lifetime, owning `drm_device`, underlying `dev_pagemap`, optional device-hold/cache/shrinker links, device memory allocation metadata, `mm_struct` association, detach completion, size, timeslice expiration, and pre-migration fence. No persistent storage exists. The CONFIG_ZONE_DEVICE stubs make calls harmless no-ops or NULL returns when device pages are unavailable.

## Dependencies and integration points
The header depends on `linux/hmm.h`, `memremap.h`, DMA direction definitions, `dev_pagemap`, page/folio zone-device data, DRM device ownership, and dma-fence synchronization. It integrates with GPU SVM, HMM migration, device-private memory providers, shrinker/cache helpers, peer interconnect mapping, and driver unbind/runtime power handling.

## Risks and test signals
Risks include stale device references after unbind, migration while hardware is removed, incorrect DMA direction/order encoding, copying ranges where only the head entry carries a higher order mapping, destroy callbacks called from reclaim context, and same-pagemap peer migration policy mistakes. Test signals include CONFIG_ZONE_DEVICE on/off builds, migrate-to-device and evict-to-RAM paths, device-unbind migration fallback, fence-delayed migration, higher-order mappings, NULL/stub behavior, and lockdep/reclaim-context teardown coverage.
