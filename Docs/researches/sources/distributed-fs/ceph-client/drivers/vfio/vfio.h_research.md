<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/vfio.h

## Purpose
This internal VFIO header defines core-private interfaces shared among VFIO main, group, container, iommufd, cdev, debugfs, and virqfd components. It abstracts optional Kconfig features behind real prototypes or stubs.

## Important APIs, types, and functions
Important types include `struct vfio_device_file`, `enum vfio_group_type`, `struct vfio_group`, `struct vfio_iommu_driver_ops`, and `struct vfio_iommu_driver`. It declares device registration refs, device file operations, group/container attach and pin APIs, iommufd bind/attach helpers, cdev helpers, virqfd init/exit, KVM association helpers, and debugfs hooks.

## Control flow
VFIO core and submodules include this header to call feature-specific operations without open-coding `#ifdef` at each call site. When a feature is disabled, inline stubs return `-EOPNOTSUPP`, false, true, or no-op as appropriate so callers can keep a uniform control flow.

## State and persistence behavior
The header declares the shape of in-memory state but does not allocate it. `vfio_device_file` tracks an opened VFIO device fd, group association, iommufd context, access-granted bit, KVM pointer, and cdev device id. `vfio_group` tracks group device state, container/iommufd association, device list, cdev open count, KVM pointer, and locking.

## Dependencies and integration points
It depends on Linux file/device/cdev/module/vfio types and optionally on `CONFIG_VFIO_GROUP`, `CONFIG_VFIO_CONTAINER`, `CONFIG_IOMMUFD`, `CONFIG_VFIO_DEVICE_CDEV`, `CONFIG_VFIO_VIRQFD`, `CONFIG_KVM`, and `CONFIG_VFIO_DEBUGFS`. It is the central contract between VFIO core and IOMMU backend drivers.

## Risks and test signals
Risks include stub behavior masking missing feature support, lock ownership assumptions around group/device set paths, and ABI changes in device-file handling. Test signals include build matrices with each optional VFIO config on/off, group and cdev open paths, iommufd bind failures, KVM set/clear, and virqfd-disabled platform IRQ builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio.h -->
