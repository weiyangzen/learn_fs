# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/pages.c

## Purpose
`pages.c` is the PFN storage and movement engine for iommufd. It backs `struct iopt_pages`, which represents a linear PFN array sourced from userspace memory, a memfd/file, or a dma-buf, and moves PFNs between three storage tiers: the `pinned_pfns` xarray for in-kernel access, IOMMU domains, and the original source.

## Important APIs, Types, And Functions
Key exported/internal APIs include `iopt_alloc_user_pages()`, `iopt_alloc_file_pages()`, `iopt_alloc_dmabuf_pages()`, `iopt_release_pages()`, `iopt_pages_update_pinned()`, `iopt_area_fill_domain()`, `iopt_area_fill_domains()`, `iopt_area_unfill_domain()`, `iopt_area_unfill_domains()`, `iopt_pages_fill_xarray()`, `iopt_pages_fill_from_xarray()`, `iopt_pages_rw_access()`, `iopt_area_add_access()`, and `iopt_area_remove_access()`. Internal helpers include the double-span interval iterator, `struct pfn_batch`, user/file/dma-buf PFN readers, and xarray/domain transfer helpers.

## Control Flow
Mapping a new area into domains locks the pages, builds a `pfn_reader`, reads PFNs from the best available tier, batches contiguous PFNs, and maps each batch into every domain. On failure it unmaps already-installed ranges and releases newly pinned pages. Removing a domain or area unmaps IOVA first, then unpins pages only if neither another domain nor access interval still covers them. In-kernel access fills the xarray from existing domains or the source, inserts an access interval, and removes/unpins on release. Read/write access either uses direct userspace copy fast paths or the full PFN reader slow path.

## State And Persistence
`iopt_pages` persists source ownership (`source_mm`, `source_task`, `source_user`), type-specific source data, `npages`, `npinned`, `last_npinned`, `account_mode`, `pinned_pfns`, `access_itree`, and `domains_itree`. Dma-buf pages also keep an attachment, physical vector, revoke status, and per-domain trackers. Destruction asserts all interval trees and xarrays are empty and no pins remain.

## Dependencies And Integration Points
This file integrates Linux GUP, memfd folio pinning, dma-buf dynamic attachments and revoke callbacks, VFIO PCI dma-buf mapping by symbol lookup, IOMMU map/unmap/iova-to-phys APIs, generic page-table dirty support, and iommufd access/domain code.

## Risks And Test Signals
High-risk areas are unmap-before-unpin security, accounting mode transitions, remote-mm locking, fault-injection cleanup, dma-buf revocation while mapped, contiguous-batch carry logic, large-page-disabled VFIO behavior, and xarray rollback. Tests should use selftest memory-limit/failure injection, map/unmap with overlapping access intervals, domain attach/detach under active pins, memfd and user mappings, dma-buf revoke, read/write slow paths, and dirty-page interaction.
