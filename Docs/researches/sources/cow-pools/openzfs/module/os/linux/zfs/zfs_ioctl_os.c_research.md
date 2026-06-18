# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_ioctl_os.c

## Purpose

Linux OS layer for the ZFS ioctl device and module initialization/teardown. It connects the common ZFS ioctl implementation to `/dev/zfs`, registers Linux-specific ioctls, initializes sysfs, and provides the kernel module entry points.

## VFS And Device State Helpers

- `zfs_vfs_held()` checks whether a `zfsvfs_t` has an attached superblock.
- `zfs_vfs_ref()` safely increments `s_active` with `atomic_inc_not_zero()` and returns `ESRCH` if the filesystem is gone.
- `zfs_vfs_rele()` releases the superblock with `deactivate_super()`.
- `zfsdev_private_set_state()` and `zfsdev_private_get_state()` store/retrieve `zfsdev_state_t` through `struct file.private_data`.

## /dev/zfs Operations

`zfsdev_open()` initializes per-open ZFS device state under `zfsdev_state_lock`. `zfsdev_release()` destroys that state.

`zfsdev_ioctl()` maps ioctl command to a vector number, allocates a `zfs_cmd_t`, copies it from userspace, calls `zfsdev_ioctl_common()`, copies results back, frees the command, and returns Linux negative errno values. `zfsdev_compat_ioctl()` delegates to the same function when compat ioctls are enabled.

`zfsdev_fops` wires open, release, unlocked ioctl, compat ioctl, and owner. `zfsdev_attach()` registers a misc device using static `ZFS_DEVICE_MINOR`, falling back to `MISC_DYNAMIC_MINOR` on `EBUSY`. `zfsdev_detach()` deregisters it.

## Linux-Specific Ioctls And Limits

`zfs_ioc_userns_attach()` and `zfs_ioc_userns_detach()` attach/detach datasets to Linux user namespaces through zone helpers, translating SPL `ENOTTY`/`ENXIO` into ZFS-specific user-namespace errors. `zfs_ioctl_init_os()` registers both dataset no-log ioctls with config security policy and no pool check.

`zfs_max_nvlist_src_size_os()` returns the configured max nvlist source size if set, otherwise the smaller of one quarter of RAM and 128 MiB. `zfs_ioctl_update_mount_cache()` is a no-op on Linux.

## Module Initialization

`openzfs_init_os()` calls `zfs_kmod_init()`, initializes ZFS sysfs, logs module/pool/filesystem versions and selected warnings, and stores `zfs_init_idmap`.

`openzfs_fini_os()` finalizes sysfs and the common kernel module state, then logs unload.

`openzfs_init()` initializes `zcommon`, ICP, zstd, and OS ZFS state in order, unwinding on failure. `openzfs_fini()` tears them down in reverse. Module metadata declares aliases for component modules, description, author, multiple license annotations, and version.
