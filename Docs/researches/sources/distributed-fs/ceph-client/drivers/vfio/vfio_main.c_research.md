<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_main.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/vfio_main.c

## Purpose
This is the VFIO core implementation. It manages VFIO device allocation, registration, device sets, device fd operations, migration feature ioctls, DMA logging feature ioctls, region capability chains, IRQ-set validation, KVM association, cdev/group integration, module initialization, and helper APIs used by VFIO drivers.

## Important APIs, types, and functions
Major exported functions include `_vfio_alloc_device`, `vfio_register_group_dev`, `vfio_register_emulated_iommu_dev`, `vfio_unregister_group_dev`, `vfio_df_open`, `vfio_df_close`, `vfio_mig_get_next_state`, `vfio_file_is_valid`, `vfio_file_enforced_coherent`, `vfio_file_set_kvm`, `vfio_info_cap_add`, `vfio_info_cap_shift`, `vfio_set_irqs_validate_and_prepare`, `vfio_pin_pages`, `vfio_unpin_pages`, and `vfio_dma_rw`. The global `vfio` object tracks device IDs and a pseudo filesystem mount for anonymous inodes. `vfio_device_fops` is the device fd file operation table.

## Control flow
VFIO drivers allocate devices through `_vfio_alloc_device`, which initializes IDs, pseudo-fs inode, driver private init, and device model fields. Registration sets a device set if needed, assigns a VFIO group type, enforces IOMMU cache coherency for physical IOMMU devices, adds the device/cdev, initializes registration refcounting, registers group metadata, and creates debugfs. Opening a VFIO device file increments open count under the device-set lock; the first open binds iommufd or uses the group IOMMU, then calls the driver open callback. File ioctls require `access_granted`, runtime-PM resume, and dispatch built-in feature/region operations before driver-specific ioctls. Unregister blocks new opens, removes cdev/device visibility, requests userspace release while waiting for refs, then removes debugfs and group state.

## State and persistence behavior
State is in memory: device IDs, device sets in an xarray, per-device refcount/open count, pseudo-fs inode, access-granted bit, KVM pointer, cdev/group/iommufd association, and optional migration/logging state fields inside `struct vfio_device`. There is no disk persistence. Module parameters include unsafe no-IOMMU enablement when configured.

## Dependencies and integration points
The file integrates almost every VFIO subsystem: group, container, iommufd, cdev, virqfd, debugfs, KVM, runtime PM, IOMMU, pseudo filesystem, and driver-supplied `vfio_device_ops`. Userspace ABI is through VFIO device file operations and feature ioctls.

## Risks and test signals
Risks include registration/unregistration lifetime races, access gating before read/write/mmap/ioctl, optional migration FSM correctness, DMA logging range validation, and KVM symbol-get lifetime. Test signals include group and cdev open paths, repeated unregister while fd is open, migration state matrix, feature probe/get/set combinations, region capability sizing, IRQ validation data-size calculations, no-IOMMU taint/permissions, runtime PM failure, `vfio_pin_pages`/`vfio_dma_rw` through container and iommufd paths, and module init/cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/vfio_main.c -->
