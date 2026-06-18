# sources/distributed-fs/ceph-client/drivers/vfio/device_cdev.c

## Purpose

`device_cdev.c` implements the VFIO device character-device path `/dev/vfio/devices/vfioX`. This is the newer IOMMUFD-centric interface where userspace opens a device cdev directly, binds it to an iommufd, and attaches or detaches IO address spaces without first opening a legacy VFIO group.

## Important APIs, Types, and Functions

`vfio_init_device_cdev()` assigns the device cdev number and initializes `device->cdev`. `vfio_device_fops_cdev_open()` creates a `vfio_device_file`, stores it as file private data, and points file mappings at the device pseudo-inode mapping. `vfio_df_ioctl_bind_iommufd()` handles `VFIO_DEVICE_BIND_IOMMUFD`, including token UUID checks, iommufd context acquisition, KVM reference capture, device open, device id return, and access grant publication. `vfio_df_unbind_iommufd()` closes and unbinds on file release. `vfio_df_ioctl_attach_pt()` and `vfio_df_ioctl_detach_pt()` call device ops for IOAS attach/detach, including PASID variants. `vfio_cdev_init()` and cleanup allocate the major/minor range.

## Control Flow

Opening a device cdev only allocates a device file and pins registration; actual device access is blocked until bind succeeds. Bind is rejected for group-backed device files, blocks legacy group opens through `vfio_device_block_group()`, serializes on the device set lock, verifies the device is not already open through this file, checks optional token UUID, gets an iommufd context from the user fd, obtains a safe KVM reference, opens the VFIO device, copies the device id back to userspace, marks `device->cdev_opened`, and uses release-store to publish `access_granted`. Failure unwinds close, KVM, iommufd, lock, and group block state.

Attach/detach parse fixed-size UAPI structs, validate flags, optionally parse PASID fields, and call the relevant VFIO device ops under `dev_set->lock`. If attaching succeeds but copying the resulting `pt_id` fails, the code detaches before returning `-EFAULT`.

## State and Persistence Behavior

The file manages transient per-open `vfio_device_file` state: `iommufd`, `devid`, KVM reference, and `access_granted`. Device-wide `cdev_opened` and legacy group block counts prevent simultaneous incompatible access paths. Nothing is file-backed; IOAS attachments live in the iommufd/device binding.

## Dependencies and Integration Points

It depends on VFIO core device-file helpers, IOMMUFD context APIs, token matching from device ops, KVM reference helpers, cdev allocation, and physical/emulated iommufd ops implemented in `iommufd.c`.

## Risks and Edge Cases

The cdev path must remain mutually exclusive with the group path. Bind blocks group access before opening and must always unblock on failure or unbind. `access_granted` uses release/acquire semantics with generic VFIO fops, so any changes must preserve ordering. PASID attach copy-to-user failure detaches through `device->ops->detach_ioas()` even when the attach was PASID-specific; this path should be checked against device ops expectations. Token UUID matching has three modes: no token support, required no-token match, and explicit user UUID.

## Test Signals

Test cdev open during unregister, bind with invalid fd/flags/argsz, token success/failure, duplicate bind, group-file rejection, group-open mutual exclusion, iommufd context failure, open-device failure unwind, attach/detach IOAS, attach/detach PASID, copy-to-user failure detach, unbind on release, and memory-ordering access checks in read/write/mmap/ioctl after bind.
