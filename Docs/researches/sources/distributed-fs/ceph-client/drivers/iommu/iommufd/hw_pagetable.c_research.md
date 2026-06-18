# sources/distributed-fs/ceph-client/drivers/iommu/iommufd/hw_pagetable.c

## Purpose
This file allocates, finalizes, aborts, destroys, configures, and invalidates IOMMUFD hardware page table objects. It supports paging HWPTs tied to IOAS objects, nested HWPTs tied to parent HWPTs or vIOMMUs, dirty tracking, dirty bitmap retrieval, page-fault queue association, and driver-specific cache invalidation.

## Important APIs, Types, And Functions
Lifecycle functions include `iommufd_hwpt_paging_destroy()`, `iommufd_hwpt_paging_abort()`, `iommufd_hwpt_nested_destroy()`, `iommufd_hwpt_nested_abort()`, and private `__iommufd_hwpt_destroy()`.

Allocation functions include `iommufd_hwpt_paging_alloc()`, `iommufd_hwpt_nested_alloc()`, `iommufd_viommu_alloc_hwpt_nested()`, and ioctl entry `iommufd_hwpt_alloc()`.

Dirty/invalidate ioctls include `iommufd_hwpt_set_dirty_tracking()`, `iommufd_hwpt_get_dirty_bitmap()`, and `iommufd_hwpt_invalidate()`.

`iommufd_hwpt_paging_enforce_cc()` asks a domain to enforce cache coherency if a bound device requires it.

## Control Flow
Paging allocation validates flags and driver capabilities, checks dirty tracking capability, rejects conflicting fault/nest-parent flags, allocates an IOMMUFD paging object, references the IOAS, allocates a domain using driver flag-aware ops or generic paging allocation, marks the domain owner and IOMMUFD cookie, enforces cache coherency if required, optionally immediately attaches the domain to support legacy drivers, fills the domain from the IOAS via `iopt_table_add_domain()`, and links it to `ioas->hwpt_list`.

Nested allocation validates user data and driver nested-domain ops, requires a non-auto paging parent marked nest-parent and owned by the same IOMMU ops, allocates a nested object, references the parent, allocates a nested domain, and verifies the domain type is `IOMMU_DOMAIN_NESTED`. vIOMMU nested allocation follows the vIOMMU ops path and references the vIOMMU.

The `iommufd_hwpt_alloc()` ioctl obtains the device and parent PT object, dispatches to paging, nested, or vIOMMU nested allocation, optionally attaches a fault object and IOPF handler, responds with the HWPT ID, and finalizes or aborts the object with proper mutex/object cleanup.

Dirty tracking validates flags, gets a paging HWPT, and delegates to `iopt_set_dirty_tracking()`. Dirty bitmap retrieval validates flags/reserved fields and delegates to `iopt_read_and_clear_dirty_data()`. Invalidate dispatches to nested-domain `cache_invalidate_user()` or vIOMMU `cache_invalidate()` and reports how many entries the driver processed.

## State And Persistence
State includes IOMMUFD HWPT objects, `iommu_domain` pointers, IOAS user refs, parent/vIOMMU refs, IOAS `hwpt_list` membership, domain cookies, fault object refs, and driver-domain dirty tracking state. All state is in kernel memory and hardware IOMMU configuration until destroyed.

## Dependencies And Integration Points
The file depends on IOMMU core domain allocation and free APIs, per-driver `iommu_ops`, nested domain ops, IOAS/page-table fill/remove logic, IOMMUFD object management, fault event queues, vIOMMU ops, and UAPI structs in `linux/iommufd.h`.

## Risks
Allocation has complex unwind paths: IOAS mutex ownership, immediate attach, domain fill, object abort/finalize, and reference counts must stay balanced. Cache coherency is security-critical; a device requiring enforced coherency must not share a non-coherent HWPT.

Nested domains require exact driver ownership compatibility and valid user data. Accepting auto domains as nesting parents or mismatched ops would let userspace construct invalid hardware nesting.

Dirty tracking assumes domain `dirty_ops` are coherent with the IOAS mappings and that enabling starts from a clean snapshot. Invalidation returns partial completion counts, so userspace must handle short processing.

## Test Signals
Test paging allocation with generic and flag-aware driver ops, dirty-tracking-capable and incapable devices, fault queue association, immediate attach failure unwind, IOAS fill failure, nested allocation with invalid parent/auto parent/mismatched ops, vIOMMU nested allocation, dirty tracking enable/disable, dirty bitmap with clear/no-clear, and invalidate dispatch with nested HWPT and vIOMMU objects.
