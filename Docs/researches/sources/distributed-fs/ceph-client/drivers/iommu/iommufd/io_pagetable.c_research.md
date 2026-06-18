# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/io_pagetable.c

## Purpose
This file implements the IOMMUFD IO page table (`io_pagetable`) that maps IOVA ranges to `iopt_pages` backing storage, fills/unfills attached IOMMU domains, supports userspace/file/DMA-BUF mappings, tracks allowed and reserved IOVA ranges, handles dirty tracking, supports unmap notifications for access objects, manages IOVA alignment, and controls large-page behavior.

## Important APIs, Types, And Functions
`struct iopt_pages_list` is a temporary map/copy descriptor pairing an `iopt_pages` object, optional `iopt_area`, start byte, length, and list node.

Contiguous-area iteration is implemented by `iopt_area_contig_init()` and `iopt_area_contig_next()`.

Map APIs include `iopt_map_user_pages()`, `iopt_map_file_pages()`, `iopt_map_pages()`, and internal `iopt_map_common()`, `iopt_alloc_area_pages()`, `iopt_insert_area()`, and `iopt_fill_domains_pages()`.

Unmap APIs include `iopt_unmap_iova()`, `iopt_unmap_all()`, and internal `iopt_unmap_iova_range()`.

Domain APIs include `iopt_table_add_domain()`, `iopt_table_remove_domain()`, `iopt_fill_domain()`, and `iopt_unfill_domain()`.

Dirty tracking APIs include `iopt_set_dirty_tracking()`, `iopt_read_and_clear_dirty_data()`, `iommufd_check_iova_range()`, and the bitmap iteration callbacks.

IOVA policy APIs include `iopt_set_allow_iova()`, `iopt_reserve_iova()`, `iopt_remove_reserved_iova()`, and `iopt_table_enforce_dev_resv_regions()`.

Other APIs include `iopt_init_table()`, `iopt_destroy_table()`, `iopt_get_pages()`, `iopt_cut_iova()`, `iopt_enable_large_pages()`, `iopt_disable_large_pages()`, `iopt_add_access()`, and `iopt_remove_access()`.

## Control Flow
Mapping begins by allocating `iopt_pages` from user VA, file, or DMA-BUF. `iopt_alloc_area_pages()` preallocates areas, takes the write side of `iova_rwsem`, validates fixed IOVA or auto-allocates a hole using allowed, reserved, and mapped interval trees, inserts areas with `pages == NULL` to reserve the IOVA space, then releases the lock. `iopt_map_pages()` fills every attached domain under `domains_rwsem`, then publishes `area->pages` under `iova_rwsem`, moving page refs from the temporary list into persistent areas.

Auto IOVA allocation preserves page offset and useful alignment for huge pages, refuses zero IOVA, scans allowed ranges or the full usable space, and uses `interval_tree_for_each_double_span()` over reserved and area trees to find a hole.

Unmap takes `domains_rwsem` read and `iova_rwsem` write. It refuses partial-area unmaps, mappings under construction/destruction, and locked areas. If an area has active access users, it marks `prevent_access`, drops locks, calls `iommufd_access_notify_unmap()`, and retries, aborting after repeated non-response. Once safe, it clears `area->pages`, unmaps/unfills domains, removes the area, drops page refs, and advances the search start to avoid racing new allocations behind it.

Domain add takes domain and IOVA write locks, checks duplicate domains, calculates required IOVA alignment from `pgsize_bitmap`, reserves geometry outside the aperture, reserves an xarray ID, fills the new domain from every existing area, updates alignment, and stores the domain. Domain removal compresses the domains xarray, unmaps/unfills the removed domain, removes its geometry reservations, and recalculates alignment.

When filling domains, a first domain can become the `storage_domain` for each area and insert the area's pages interval into `pages->domains_itree`. Later domains can be filled from page storage. Removing one of many domains may select another storage domain, while removing the last domain fully unpins/unfills from page storage. DMA-BUF areas also track/untrack revocation per domain.

Dirty tracking validates bitmap ranges against IOAS alignment and bitmap page size, iterates only contiguous mapped IOVA areas, calls driver dirty ops, and syncs IOTLB gathers when clearing. Enabling dirty tracking first clears existing dirty data to start from a clean baseline.

Allowed IOVA replacement swaps the allowed interval tree and verifies no reserved range intersects. Reserved IOVA insertion refuses overlap with mapped areas or allowed ranges, records an owner, and removal deletes all owner-matching reservations. Device reserved-region enforcement imports IOMMU reserved regions, skips relaxable direct regions, reserves all other regions, records SW-MSI base when requested, and validates HW/SW MSI combinations.

Area splitting for VFIO compatibility creates left/right areas around a split point, disallows DMA-BUF, active access, huge-page-capable mapped domains unless large pages are disabled, updates `pages->domains_itree`, and shares the same `iopt_pages` via refcounts.

## State And Persistence
Persistent runtime state inside `io_pagetable` includes interval trees for mapped areas, allowed IOVAs, and reserved IOVAs; an xarray of attached domains; an xarray of access users; `iova_alignment`; `next_domain_id`; and large-page mode. Each `iopt_area` stores IOVA range, backing page range, permissions, page offset, storage domain, access counters, lock counters, and access-prevention state. Backing `iopt_pages` objects and domain page tables persist until unmapped or domains are removed.

## Dependencies And Integration Points
This file depends on `pages.c` for pinning, filling domains, xarray page storage, DMA-BUF tracking, access pinning, and rw access; on `ioas.c` for ioctl entry points; on `hw_pagetable.c` for domain add/remove and dirty tracking; on `device.c` for reserved regions and access notifications; on IOMMU core map/unmap/dirty ops; and on interval tree, xarray, DMA-BUF, and UAPI bitmap helpers.

## Risks
Locking is dense: `iova_rwsem` protects IOVA interval structures, `domains_rwsem` prevents domain attach/remove while areas are transient, and `pages->mutex` protects page storage, `storage_domain`, and access counters. Lock order regressions can deadlock or expose NULL `pages` areas to domain attach.

Publishing areas with `pages == NULL` reserves IOVA during setup; any user of `area->pages` must honor the documented lock rules. Unmap must notify and wait for external access users; non-cooperating users can stall unmap or trigger `-EDEADLOCK`.

Alignment changes from domains, access objects, and large-page mode can reject existing mappings. Area splitting is intentionally constrained because huge pages, DMA-BUF revocation, and access intervals are hard to split safely.

Reserved region enforcement must avoid overflow in `start + length - 1`, handle driver-provided regions sanely, and unwind owner reservations on failures. Dirty bitmap code must reject unaligned or overflowing ranges to avoid reading outside mappings.

## Test Signals
Test fixed and auto IOVA map/unmap, overlap rejection, reserved/allowed range interaction, aperture reservations, multiple attached domains, domain add/remove while mappings exist, map failure unwind, DMA-BUF mappings and revocation, dirty tracking enable and bitmap read with no-clear/clear, unmap with active access callbacks, `iopt_get_pages()` contiguous coverage, area splitting with large pages enabled/disabled, access-list alignment changes, and destroy-time empty-tree/xarray warnings.
