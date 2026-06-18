# sources/distributed-fs/ceph-client/drivers/vfio/group.c

## Purpose

`group.c` implements the legacy VFIO group device `/dev/vfio/$GROUP` and group lifecycle. VFIO groups collect devices sharing an IOMMU group, expose ioctls to set a container or iommufd compatibility context, provide device fds by name, and coordinate mutual exclusion with the direct cdev path.

## Important APIs, Types, and Functions

Key routines are `vfio_group_ioctl_set_container()`, `vfio_group_ioctl_unset_container()`, `vfio_group_ioctl_get_device_fd()`, `vfio_group_ioctl_get_status()`, `vfio_device_open_file()`, `vfio_df_group_open()`, `vfio_df_group_close()`, `vfio_device_block_group()`, `vfio_device_unblock_group()`, `vfio_device_set_group()`, `vfio_device_remove_group()`, `vfio_device_group_register()`, and `vfio_group_init()/cleanup()`. Global state tracks `group_list`, `group_lock`, an IDA for minors, and the char-device major.

## Control Flow

Group creation happens when a VFIO device registers. The driver finds an existing group by `iommu_group` or allocates a new cdev-backed group; no-IOMMU can synthesize an IOMMU group and taint the kernel. Opening `/dev/vfio/$GROUP` requires active drivers, CAP_SYS_RAWIO for no-IOMMU, no cdev-opened devices, and no existing group open. `SET_CONTAINER` accepts either a legacy container fd or an iommufd; the latter creates a compatibility IOAS. `GET_DEVICE_FD` finds the device by driver match or device name, allocates a `vfio_device_file`, opens the device under group and device-set locks, attaches a compat IOAS for iommufd groups on first open, and returns an anon inode device fd.

On group fd release, any attached legacy container or iommufd is detached and the group becomes unopened. When the final driver leaves a group, `vfio_device_remove_group()` removes the cdev, detaches any container, nulls the IOMMU group to block new users, drops references, and frees the group device.

## State and Persistence Behavior

Groups persist while at least one VFIO device driver is registered in the group. State includes the underlying `iommu_group`, device list, group/container/iommufd pointers, container user count, KVM pointer, open group file, cdev open count, and driver refcount. This is all in-kernel lifetime state. No-IOMMU groups are synthetic and removed when the device unregisters.

## Dependencies and Integration Points

The file integrates legacy containers from `container.c`, iommufd compatibility helpers, VFIO device-file core, KVM pointer handling, IOMMU group APIs, anon inodes, character devices, and exported helpers used by KVM/SPAPR and other VFIO code.

## Risks and Edge Cases

The group path and cdev path are mutually exclusive through `opened_file` and `cdev_device_open_cnt`. Races around unregister are handled by `drivers` refcount and group locks; tests should stress device removal during group open/get-device-fd. With iommufd compatibility, `GET_STATUS` can show viable before `GET_DEVICE_FD` fails due to DMA-owner claim, as documented in comments. No-IOMMU access must enforce CAP_SYS_RAWIO and reject compat IOAS use. The device fd holds references transferred from device registration and group file references.

## Test Signals

Test group creation/reuse, duplicate device in group warning path, no-IOMMU synthetic group creation and taint, group open exclusivity, cdev/group mutual exclusion, status flags before/after container/iommufd, set/unset container, get-device-fd success/failure, KVM reference capture/release, iommufd compat attach, group remove while users exist, SPAPR `vfio_file_iommu_group()`, and cleanup with empty group list.
