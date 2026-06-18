# sources/distributed-fs/ceph-client/include/linux/iommu.h

Purpose: This is the central Linux IOMMU API header, defining domain types, protection flags, device/group abstractions, fault reporting, dirty tracking, PASID/SVA/IOPF hooks, and driver operation tables.

Important APIs, types, and functions: Key types include `iommu_domain`, `iommu_ops`, `iommu_domain_ops`, `iommu_device`, `dev_iommu`, `iommu_group`, `iommu_resv_region`, `iommu_iotlb_gather`, `iommu_dirty_bitmap`, `iommu_user_data`, `iopf_queue`, and `iopf_group`. Public APIs cover domain allocation/free, attach/detach, map/unmap/map_sg, IOVA translation, reserved regions, group management, default domain use, DMA ownership claims, PASID attach/detach, SVA bind/unbind, IOPF queueing, page responses, dirty tracking, and MSI cookie preparation.

Control flow: IOMMU drivers register `iommu_device` instances with `iommu_ops`. Core code probes devices, groups them, allocates domains, attaches devices or PASIDs, and routes map/unmap calls to domain ops. IOTLB gather helpers batch invalidation ranges and sync when granularity changes or ranges become disjoint. Fault paths collect page requests into groups and respond through device/queue handlers.

State and persistence: Domains hold type, owner ops, page-size bitmap, geometry, cookie union, and optional dirty/fault handlers. Devices hold `dev_iommu` state including fwspec, private data, fault params, and flags. Groups and global PASIDs persist until explicit release. SVA domains link into mm-associated data.

Dependencies and integration points: Integrates with devices, buses, firmware nodes, OF, PCI, MSI, scatterlists, mm, iommufd UAPI, IOVA bitmaps, debugfs, lockdep, and optional CONFIG stubs.

Risks: Domain type flags must match operation support. Missing TLB sync after unmap can leave stale DMA translations. User-data copy helpers enforce type and length for ABI compatibility; misuse can reject valid extensions or accept invalid buffers. Non-IOMMU configs return stubs that often report `-ENODEV`.

Test signals: Cover every domain type, map/unmap/TLB gather, attach error codes, group lifetime, reserved-region merging, dirty tracking, PASID/SVA, IOPF fault response, iommufd user data copy, non-IOMMU stubs, MSI isolation, and lockdep assertions.
