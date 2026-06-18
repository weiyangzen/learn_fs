# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/iommu.h

Purpose: Declares PowerPC IOMMU/TCE table structures, table/group operations, DMA mapping helpers, VFIO-style TCE exchange APIs, and early platform initialization hooks.

Important APIs, types, and functions: Defines IOMMU page macros, DMA window property names, `iommu_table_ops`, `iommu_pool`, `iommu_table`, `iommu_table_group_ops`, `iommu_table_group`, table reference/init/clear/reserve helpers, group registration/device attach, TCE exchange/kill/check/flush/direction helpers, DMA map/unmap/coherent APIs, early pSeries/DART/PASEMI init, and `dma_iommu_ops`.

Control flow: Platform setup creates tables/groups, devices attach to a group, DMA mapping allocates TCE ranges from pools, writes TCEs through table ops, flushes as needed, and unmap/free returns ranges. VFIO/userspace paths exchange TCEs after parameter checks.

State and persistence: `iommu_table` stores page shift, offset, size, pools, locks, reference count, userspace ownership, and ops. Groups link tables to devices. State is runtime memory plus hardware TCE tables.

Dependencies and integration points: Integrates DMA API, PCI/pSeries/DART platform code, VFIO/IOMMU userspace mappings, device-tree DMA windows, and memory hotplug/restore.

Risks: TCE address/permission checks protect DMA isolation. Pool allocation must be synchronized. Userspace-owned entries need careful RO/permission handling. Early boot init order affects all DMA.

Test signals: DMA map/unmap/coherent allocation, scatter-gather boundaries, TCE userspace exchange failures, table refcounting, group attach/detach, IOMMU off/force-on modes, and suspend restore.
