# sources/distributed-fs/ceph-client/drivers/vfio/Kconfig

## Purpose

This Kconfig file defines the top-level VFIO framework options and includes bus-specific VFIO submenus. It controls whether VFIO core support, legacy group/container access, cdev/iommufd access, no-IOMMU support, virqfd, debugfs, and PCI/platform/mdev/fsl-mc/cdx drivers are available.

## Important APIs, Types, and Functions

The main option is `menuconfig VFIO`. It selects `IOMMU_API` and `INTERVAL_TREE`, conditionally selects `VFIO_GROUP`, `VFIO_DEVICE_CDEV`, and `VFIO_CONTAINER`, and includes help text describing VFIO as a secure userspace device-driver framework. Suboptions define `VFIO_DEVICE_CDEV`, `VFIO_GROUP`, `VFIO_CONTAINER`, `VFIO_IOMMU_TYPE1`, `VFIO_IOMMU_SPAPR_TCE`, `VFIO_NOIOMMU`, `VFIO_VIRQFD`, and `VFIO_DEBUGFS`.

## Control Flow

Configuration flow is conditional on `VFIO`. If VFIO is enabled, users can select the cdev interface when IOMMUFD is available without SPAPR TCE, the traditional group interface, the legacy container interface, no-IOMMU mode, and debugfs. The file then sources bus-specific Kconfig files and `virt/lib/Kconfig`.

## State and Persistence Behavior

The file creates build-time configuration state only. Its choices persist in `.config` and determine which objects are built and which runtime interfaces exist.

## Dependencies and Integration Points

It ties VFIO to IOMMUFD, SPAPR TCE, architecture-specific IOMMU drivers, DEBUG_FS, and bus-specific VFIO directories. The options map directly to object lists in `drivers/vfio/Makefile`.

## Risks and Edge Cases

The conditional defaults decide user ABI availability. For example, `VFIO_DEVICE_CDEV` defaults on only when groups are not selected, `VFIO_CONTAINER` depends on groups, and no-IOMMU requires group support. Misconfigured dependencies could expose no usable VFIO access path or accidentally disable the legacy ABI expected by userspace.

## Test Signals

Kconfig tests should cover VFIO with IOMMUFD enabled/disabled, SPAPR TCE, no-IOMMU, DEBUG_FS, and each bus submenu. Build configs should verify that selected symbols pull the intended objects and that mutually dependent cdev/group/container paths remain coherent.
