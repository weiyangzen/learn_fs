# sources/distributed-fs/ceph-client/drivers/xen/unpopulated-alloc.c

## Purpose
`unpopulated-alloc.c` provides allocation and free helpers for Xen unpopulated pages: guest physical pages that have `struct page` backing but no real machine memory populated until mapped or granted. These are used by foreign mapping paths such as privcmd and other Xen drivers.

## Important APIs, types, and functions
Exports are `xen_alloc_unpopulated_pages` and `xen_free_unpopulated_pages`. `arch_xen_unpopulated_init` is a weak architecture hook that selects the resource tree for scratch address allocation. Internals include global `page_list`, `list_count`, `target_resource`, `xen_unpopulated_pages`, and `fill_list`, which reserves IOMEM ranges and creates generic device pages through `memremap_pages`.

## Control flow
Early init selects a target resource for scratch ranges. Allocation falls back to ballooned pages if no target resource is available. Otherwise it fills the freelist by allocating a pluggable IOMEM resource, optionally reserving the same range in `iomem_resource`, initializing PV p2m entries to invalid, and using `memremap_pages` to create page structures. Pages are popped under a mutex and, on PV, p2m entries are allocated before returning. Freeing pushes pages back to the global list.

## State and persistence
The module maintains a runtime freelist of unpopulated device pages protected by `list_lock`. Resource reservations and dev_pagemap ownership persist for the boot lifetime, but there is no on-disk persistence.

## Dependencies and integration points
It depends on memory hotplug resource APIs, `memremap_pages`, Xen balloon APIs, Xen p2m operations under PVMMU, and architecture-provided resource selection. It integrates with `privcmd.c` and other Xen code needing placeholder pages for foreign mappings.

## Risks and test signals
Risks include resource leaks on partial `fill_list` failure, p2m invalidation assumptions, fallback differences when no target resource exists, section-size rounding, holding stale device-page metadata in `zone_device_data`, and concurrent allocation/free. Test signals include allocation/free stress, PV and HVM guests, memory hotplug configs, failure injection in resource allocation and `memremap_pages`, privcmd foreign mapping teardown, and balloon fallback behavior.
