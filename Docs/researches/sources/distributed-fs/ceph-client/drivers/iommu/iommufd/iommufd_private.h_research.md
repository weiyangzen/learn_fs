# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/iommufd_private.h

## Purpose
`iommufd_private.h` is the internal contract for the iommufd driver. It defines the context object, IO page-table abstraction, user command carrier, object lifetime helpers, and the object families used by IOAS, hardware page tables, devices, access objects, fault queues, vIOMMU objects, virtual devices, vevent queues, and hardware queues.

## Important APIs, Types, And Functions
`struct iommufd_ctx` owns the file, object xarray, group xarray, destroy waitqueue, IOAS creation lock, mmap maple tree, software MSI state, accounting mode, VFIO no-IOMMU mode, and compat IOAS pointer. `struct io_pagetable` owns domain/access xarrays and interval trees for mapped areas, allowed IOVAs, and reserved IOVAs. `struct iommufd_ucmd` carries ioctl context and automatic object creation state. Inline helpers wrap object lookup and put semantics, including `iommufd_get_ioas()`, `iommufd_get_device()`, `iommufd_get_hwpt_paging()`, `iommufd_get_viommu()`, and similar typed accessors.

## Control Flow
The header establishes the object allocation/finalization protocol: `_iommufd_object_alloc()` reserves an xarray slot, callers initialize privately, and `iommufd_object_finalize()` publishes the pointer. Ucmd allocators defer finalization or abort to the ioctl dispatcher. Destruction helpers either remove an object, tombstone an ID, or attempt auto-destroy for auto-domain HWPTs.

## State And Persistence
All persistent kernel state is rooted in `iommufd_ctx::objects`. Object refcounting uses `users` for live users and `wait_cnt` for deterministic destruction. IOAS state persists through `struct iommufd_ioas` and `struct io_pagetable`; vIOMMU state persists through `struct iommufd_viommu` relationships to HWPTs, vdevices, and event queues.

## Dependencies And Integration Points
The header binds together Linux IOMMU core types, uapi structures, xarrays, maple trees, interval trees, access APIs exported to in-kernel users, fault/event queue dispatch, and optional `CONFIG_IOMMUFD_TEST` hooks. It also declares VFIO compatibility and software MSI support.

## Risks And Test Signals
The main risks are API contract drift between object types, refcount imbalance, lock-order mismatch with `domains_rwsem -> iova_rwsem -> pages::mutex`, and incorrect inline helper type assumptions. Tests should exercise object creation abort/finalize paths, auto-domain lifetime, access detach/destroy, vIOMMU event queue lookup, selftest-disabled stubs, and all ioctl handlers declared here.
