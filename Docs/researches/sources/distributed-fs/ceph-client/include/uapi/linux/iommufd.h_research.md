# sources/distributed-fs/ceph-client/include/uapi/linux/iommufd.h

## Purpose
`iommufd.h` defines the userspace ABI for the IOMMU file descriptor subsystem. It exposes object IDs and ioctl structures for managing IO address spaces, hardware page tables, virtual IOMMUs, virtual devices, fault queues, event queues, and hardware-assisted queues used by VFIO, VMMs, and device assignment stacks.

## Important APIs, Types, and Functions
The ioctl command enum starts at `IOMMUFD_CMD_BASE` and maps to `IOMMU_DESTROY`, `IOMMU_IOAS_ALLOC`, `IOMMU_IOAS_MAP`, `IOMMU_IOAS_UNMAP`, `IOMMU_HWPT_ALLOC`, `IOMMU_GET_HW_INFO`, dirty tracking ioctls, fault queue allocation, vIOMMU/vDEVICE allocation, vEVENTQ allocation, and HW queue allocation. Core data carriers include `iommu_ioas_map`, `iommu_ioas_copy`, `iommu_ioas_unmap`, `iommu_hwpt_alloc`, `iommu_hw_info`, `iommu_hwpt_invalidate`, `iommu_hwpt_pgfault`, `iommu_viommu_alloc`, `iommu_vdevice_alloc`, `iommu_veventq_alloc`, and `iommu_hw_queue_alloc`.

## Control Flow
Userspace opens an iommufd, allocates an IOAS, optionally constrains allowed IOVA ranges, maps user memory or memfd-backed memory, attaches devices through related kernel paths, and allocates HWPTs for kernel-managed or nested page tables. Nested flows query hardware info, allocate parent and nested HWPTs, submit invalidations after userspace page table edits, handle PRI faults via fault FDs, and report page responses. Virtualization flows allocate vIOMMU objects, vDEVICE IDs, vEVENTQs, and platform-specific HW queues.

## State and Persistence
All durable state is kernel-owned and referenced by per-iommufd object IDs or returned file descriptors. IOAS mappings pin or reference memory until unmapped or destroyed. Dirty-tracking state is toggled on HWPT objects. vEVENTQ and FAULT queues persist as FDs and may lose events under overflow. `IOMMU_DESTROY` tears down destroyable IDs; closing the iommufd or auxiliary FDs releases remaining state.

## Dependencies and Integration Points
The header depends on `<linux/ioctl.h>` and `<linux/types.h>`, and uses aligned UAPI integer types. It integrates with VFIO compatibility IOAS handling, PCI PASID/ATS/PRI concepts, Intel VT-d, ARM SMMUv3, NVIDIA Tegra241 CMDQV, AMD IOMMU, memfd-backed mappings, and VMM device assignment code.

## Risks and Test Signals
ABI risk is high: structure size/version extension relies on zeroed unknown trailing fields, reserved fields must be zero, and `__aligned_u64` layout must be stable across 32/64-bit userspace. Security-sensitive tests should cover invalid IDs, IOVA overflow, unmapped or partially mapped ranges, permission flags, dirty bitmap sizing, fault response cookies, vEVENTQ overflow markers, nested invalidation type validation, and destroy ordering for vDEVICE/vIOMMU/HW queue objects.
