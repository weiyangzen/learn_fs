# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/kmod_core.c

## Scope

FreeBSD kernel module entry point and `/dev/zfs` character device glue. It handles ioctl marshalling, per-open devfs private state, module load/unload/shutdown, and module dependency declarations.

## Main Interfaces

- `/dev/zfs` cdev operations: `zfsdev_open()` and `zfsdev_ioctl()`.
- Device lifecycle: `zfsdev_attach()` and `zfsdev_detach()`.
- Devfs private state hooks: `zfsdev_private_set_state()` and `zfsdev_private_get_state()`.
- Module lifecycle: `zfs__init()`, `zfs__fini()`, `zfs_shutdown()`, and `zfs_modevent()`.

## State And Control Flow

`zfsdev_ioctl()` validates the ioctl argument length, copies a user `zfs_cmd_t` into kernel memory, optionally translates legacy ioctl commands/structures, calls `zfsdev_ioctl_common()`, copies results back to user memory, frees temporary buffers, and verifies no rrw TSD remains.

`zfs__init()` holds root mount while initializing the ZFS kernel module, creates GEOM probe TSD storage, prints the feature-support version, releases root hold, and initializes sysevents. `zfs__fini()` refuses unload while pools/zvols/injection are busy, finalizes ZFS, and destroys GEOM probe TSD storage. Module load registers a post-sync shutdown handler; unload deregisters it after successful fini.

## Dependencies

Uses FreeBSD cdev/devfs, root mount hold, eventhandlers, module framework, ioctl compatibility code, OpenZFS `zfs_kmod_init/fini`, zvol busy checks, and GEOM probe TSD key.

## Correctness Notes

Unload is blocked while ZFS or zvol state is active. Shutdown skips fini during panic because normal teardown paths are not safe in a panicked kernel. Legacy ioctl compatibility is isolated behind `ZFS_LEGACY_SUPPORT`.
