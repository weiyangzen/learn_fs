<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic_pt/iommu.h -->
# sources/distributed-fs/ceph-client/include/linux/generic_pt/iommu.h

Purpose: Declares the IOMMU-facing API for generic radix page-table implementations, letting drivers wire format-specific page tables into `iommu_domain` operations.

Important APIs/types/functions: `pt_iommu` embeds an `iommu_domain`, generic ops, driver ops, allocation NUMA node, and IOMMU device for cache maintenance. `pt_iommu_ops` provides `map_range`, `unmap_range`, `set_dirty`, `get_info`, and `deinit`. `pt_iommu_driver_ops` provides dynamic top update hooks `change_top()` and `get_top_lock()`. `pt_iommu_cfg` carries requested features and hardware VA/OA limits. Macros generate format structs/prototypes for `amdv1`, `vtdss`, `riscv_64`, `x86_64`, and mock AMDv1, plus `IOMMU_PT_DOMAIN_OPS`, `IOMMU_PT_DIRTY_OPS`, and `PT_IOMMU_CHECK_DOMAIN()`.

Control flow: IOMMU drivers initialize a format-specific table, expose the embedded domain ops, then map/unmap through `pt_iommu_ops` while holding caller-provided VA range locks. Unmap gathers IOTLB invalidations. Dynamic top support calls driver hooks under a provided spinlock.

State and persistence behavior: Runtime state is the page table itself, domain alias, ops pointers, NUMA allocation policy, and device pointer. `pt_iommu_deinit()` is safe before successful init because it only calls `deinit` when ops is set.

Dependencies and integration points: Depends on generic page-table common definitions, IOMMU core, mm types, dirty bitmap APIs, and IOTLB gather. Integrates with DMA API, IOMMUFD, dirty tracking, and hardware domain attachment lists.

Risks: Caller must serialize overlapping VA ranges. `unmap_range()` cannot split mappings created by `map_range()`. Dynamic top requires hardware atomicity and correct lock choice. Domain aliasing via unions must pass offset checks. Atomic-context flushing constraints apply to driver ops.

Test signals: IOMMU map/unmap/iova_to_phys tests, dirty tracking including `set_dirty()` races, dynamic top growth, page-size bitmap validation, unmap aggregation boundaries, IOMMUFD selftests for mock AMDv1, and lockdep around range locks/top locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/generic_pt/iommu.h -->
