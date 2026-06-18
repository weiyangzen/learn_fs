# sources/distributed-fs/ceph-client/drivers/xen/Kconfig

## Purpose
This Kconfig file defines the Xen driver support menu. It controls memory ballooning, xenfs, event-channel device support, grant devices, backend/frontend drivers, ACPI/EFI helpers, SWIOTLB, virtio grant integration, and platform-specific Xen support options.

## Important APIs, types, and functions
It is declarative Kconfig. Important symbols include `XEN_BALLOON`, `XEN_BALLOON_MEMORY_HOTPLUG`, `XEN_DEV_EVTCHN`, `XEN_BACKEND`, `XENFS`, `XEN_GNTDEV`, `XEN_GRANT_DEV_ALLOC`, `SWIOTLB_XEN`, `XEN_PCIDEV_BACKEND`, `XEN_PRIVCMD`, `XEN_ACPI_PROCESSOR`, `XEN_MCE_LOG`, `XEN_EFI`, `XEN_AUTO_XLATE`, `XEN_ACPI`, `XEN_UNPOPULATED_ALLOC`, `XEN_VIRTIO`, and `XEN_VIRTIO_FORCE_GRANT`.

## Control flow
The menu is visible only under `XEN`. Per-feature dependencies constrain options by architecture, Dom0/backend role, PCI, ACPI, memory hotplug, target core, eventfd, virtio, DMA ops, and EFI. `select` clauses pull in required helpers such as `SWIOTLB`, `MMU_NOTIFIER`, `DMA_SHARED_BUFFER`, grant DMA ops, and IOMMU support.

## State and persistence
State is build-time `.config` state. Selected symbols drive kbuild object inclusion and preprocessor conditionals in Xen drivers.

## Dependencies and integration points
It integrates Xen guest/Dom0 subsystems with memory management, block/network/storage backends, userspace hypercall interfaces, ACPI/EFI platform services, DMA mapping, and virtio grant support.

## Risks and test signals
Risks include under-specified dependencies causing randconfig build failures, defaults enabling too much in non-Dom0 guests, hidden selects changing DMA behavior, and architecture-specific symbols being visible in impossible configurations. Test signals include `allmodconfig`, `randconfig`, x86/ARM/ARM64 Xen guest and Dom0 builds, EFI-enabled builds, and combinations of virtio grant options.
