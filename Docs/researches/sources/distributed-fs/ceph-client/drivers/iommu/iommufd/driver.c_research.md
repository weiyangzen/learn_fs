# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/driver.c

## Purpose
This file builds the driver-facing IOMMUFD helper module. It exports object dependency helpers, mmap-offset management for driver-owned MMIO windows, vIOMMU/vdevice lookup helpers, vIOMMU event reporting, and software MSI mapping support shared with builtin modules.

## Important APIs, Types, And Functions
`_iommufd_object_depend()` and `_iommufd_object_undepend()` let drivers create same-type object dependencies by manipulating object user refcounts. They reject self-dependency and cross-type dependencies.

`_iommufd_alloc_mmap()` allocates a page-aligned mmap offset in `ictx->mt_mmap` for an owner object and physical MMIO range. `_iommufd_destroy_mmap()` erases that offset and verifies ownership.

`iommufd_vdevice_to_device()`, `iommufd_viommu_find_dev()`, and `iommufd_viommu_get_vdev_id()` translate virtual devices back to physical devices or virtual IDs under vIOMMU xarray locking.

`iommufd_viommu_report_event()` queues driver-supplied vIOMMU events into a typed event queue, using a lost-events header when the queue is full or allocation fails.

When `CONFIG_IRQ_MSI_IOMMU` is enabled, `iommufd_sw_msi_get_map()`, `iommufd_sw_msi_install()`, and `iommufd_sw_msi()` create fd-global IOVA mappings for physical MSI pages and update MSI descriptors.

## Control Flow
Dependency helpers are direct refcount operations with validation.

MMAP allocation validates page alignment, allocates `struct iommufd_mmap`, reserves a range in the maple tree starting after the first page, stores `vm_pgoff`, and returns a user-visible offset. Destroy erases and frees it.

vIOMMU event reporting takes `viommu->veventqs_rwsem`, finds a queue by type, then under the queue spinlock either appends a newly allocated event or records lost events. It calls the event handler to place the event on the queue and wake readers.

Software MSI handling is invoked from the IOMMU core while the group mutex protects attach-handle lifetime. It finds the IOMMUFD attach handle, skips identity/no-software-MSI cases, allocates or reuses a global MSI-page mapping, maps the physical page into the hwpt if not present, records required MSI bits on the group, and updates the descriptor with the IOVA.

## State And Persistence
State lives in IOMMUFD context maple trees (`mt_mmap`), vIOMMU xarrays/lists, event queue lists and counters, and `sw_msi_list`/bitmaps. These are kernel-memory lifetimes tied to the IOMMUFD file and objects.

## Dependencies And Integration Points
The file depends on IOMMUFD private objects, Linux maple tree, anon event queues from `eventq.c`, vIOMMU objects, MSI descriptors, `iommu_map()`, IOMMU core attach handles, and the `IOMMUFD`/`IOMMUFD_INTERNAL` export namespaces.

## Risks
Object dependencies are low-level refcount operations; misuse can leak objects or deadlock destruction. MMAP offsets must remain owner-checked to avoid one object destroying another object's mapping.

Event reporting runs in contexts such as threaded IRQ handlers, so allocation uses atomic behavior and overflow must be represented through lost-event headers. Queue depth and lost event semantics need careful testing.

Software MSI is security-sensitive: mappings must match reserved SW-MSI windows, be consistent across domains in a context, and only run while attach handles are stable.

## Test Signals
Test same-type dependency/ref release, rejection of self and cross-type dependencies, mmap alignment and duplicate destroy warnings, vIOMMU device lookup under xarray locking, event queue overflow/lost events, and software MSI mapping reuse across devices/domains with IOMMUFD cookies.
