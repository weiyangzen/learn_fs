# sources/distributed-fs/ceph-client/include/xen/mem-reservation.h

## Purpose
`mem-reservation.h` declares Linux-side helpers for Xen memory reservation growth/shrink, optional page scrubbing, and PV MMU virtual-address mapping updates after reservation changes.

## Important APIs, Types, and Functions
Important symbols are `xen_scrub_pages`, `xenmem_reservation_scrub_page()`, `xenmem_reservation_va_mapping_update()`, `xenmem_reservation_va_mapping_reset()`, `xenmem_reservation_increase()`, and `xenmem_reservation_decrease()`. PV MMU-specific implementation hooks are declared under `CONFIG_XEN_HAVE_PVMMU`.

## Control Flow
Callers increase or decrease a reservation using frame arrays. Scrubbing clears highmem pages when `xen_scrub_pages` is enabled. On PV domains with PV MMU support, wrapper functions call architecture helpers to update or reset virtual mappings for pages whose machine frames changed.

## State and Persistence Behavior
The helpers mutate domain memory reservation and page-to-frame mappings through implementation code. `xen_scrub_pages` is a runtime policy flag; page contents are cleared only in memory and not persisted.

## Dependencies and Integration Points
It depends on Linux highmem and Xen page helpers. It integrates ballooning, memory hotplug, unpopulated page allocation, and PV MMU mapping consistency.

## Risks and Test Signals
Risks include stale virtual mappings after frame replacement, failing to scrub pages before reuse, PV/HVM domain path confusion, and partial reservation failures. Test signals include balloon inflate/deflate, highmem page scrubbing, PV mapping update/reset coverage, and memory hotplug under Xen.
