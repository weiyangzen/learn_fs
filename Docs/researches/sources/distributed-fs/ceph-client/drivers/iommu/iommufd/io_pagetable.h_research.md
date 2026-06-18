# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/io_pagetable.h

## Purpose
This header defines the core data structures and helper interfaces for IOMMUFD IO page tables. It describes how IOVA areas map to backing page objects, how allowed/reserved intervals are represented, how access and DMA-BUF tracking interact with mappings, and which functions `io_pagetable.c`, `pages.c`, `ioas.c`, `device.c`, and `hw_pagetable.c` share.

## Important APIs, Types, And Functions
`struct iopt_area` represents one mapped IOVA interval and its slice of an `iopt_pages` backing object. It contains interval-tree nodes for IOVA and pages, the parent `io_pagetable`, backing `iopt_pages`, `storage_domain`, page offset, permissions, `prevent_access`, and access/lock counters.

`struct iopt_allowed` and `struct iopt_reserved` represent allowed and reserved IOVA intervals; reserved intervals carry an owner pointer for owner-scoped removal.

Inline helpers convert between area IOVA, page indexes, lengths, and byte offsets: `iopt_area_index()`, `iopt_area_last_index()`, `iopt_area_iova()`, `iopt_area_last_iova()`, `iopt_area_length()`, `iopt_area_start_byte()`, and `iopt_area_iova_to_index()`.

The `__make_iopt_iter()` macro creates interval-tree iterators for areas, allowed ranges, and reserved ranges.

`struct iopt_area_contig_iter` and `iopt_for_each_contig_area()` define contiguous mapped-area iteration over an IOVA range.

`enum iopt_address_type` distinguishes user memory, file-backed memory, and DMA-BUF memory. `struct iopt_pages_dmabuf_track` and `struct iopt_pages_dmabuf` hold DMA-BUF attachment/tracking state.

`struct iopt_pages` stores backing memory state: kref, mutex, page count, pinned count, source task/mm/user, address type, backing pointer/file/DMA-BUF, writability, accounting mode, pinned PFN xarray, access interval tree, and domains interval tree.

Function declarations cover domain fill/unfill, DMA-BUF tracking, page allocation/release, xarray fill/unfill, access pin/unpin, rw access, and pin accounting.

## Control Flow
Callers build mappings by allocating an `iopt_pages`, inserting one or more `iopt_area` entries, filling attached domains through declared fill functions, and then publishing the area as active. Access and unmap paths use byte/index helpers to translate from IOVA ranges to backing pages. Domain add/remove paths use domain fill/unfill declarations and DMA-BUF tracking declarations. Page pinning and CPU rw access are implemented in `pages.c` behind the prototypes in this header.

The header encodes important lock expectations in comments: `io_pagetable::iova_rwsem` protects interval nodes, `iopt_pages::mutex` protects page nodes and access counters, `iopt` and permissions are immutable, and `storage_domain` is protected by `pages->mutex`.

## State And Persistence
The header defines runtime in-memory state only. `iopt_area` and `iopt_pages` objects persist while IOAS mappings or access pins reference them. Xarray and interval-tree nodes are embedded in those objects rather than stored separately.

## Dependencies And Integration Points
It depends on DMA-BUF, interval tree, kref, mutex, xarray, IOMMU domain declarations, and `iommufd_private.h`. Its structures are shared by `io_pagetable.c` for IOVA layout, `pages.c` for PFN storage and domain map/unmap, `device.c` for access objects, `hw_pagetable.c` for dirty tracking/domain registration, and `ioas.c` for userspace IOAS commands.

## Risks
The structure comments are part of the contract. Misusing `area->pages == NULL`, `storage_domain`, or interval nodes outside the documented locks risks races during map/unmap or domain attach/remove.

Byte/index conversion must preserve page offsets for sub-page-aligned file or user mappings. Incorrect conversions can pin or expose the wrong backing pages.

DMA-BUF revocation is represented by zero-length `phys` state and must be checked while holding `pages->mutex`; otherwise mappings may outlive revoked attachments.

Access intervals act as locks over pinned PFNs. Incorrect access accounting can prevent unmap forever or allow unmap while a driver still uses pages.

## Test Signals
Compile-time signals include lockdep assertions and selftest warnings in helpers. Runtime tests should cover byte/index conversions with offsets, contiguous iteration gaps, access interval add/remove accounting, DMA-BUF revoked checks, page refcount release, domain fill/unfill declarations across multiple domains, and alignment changes caused by domains or access objects.
