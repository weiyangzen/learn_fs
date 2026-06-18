# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ioctl_os.c

## Purpose

Provides FreeBSD-specific ioctl helpers and platform ioctl registration for OpenZFS. It handles VFS hold/release glue, jail/unjail dataset ioctls, FreeBSD nextboot label writes, mount stat cache updates, and OS-specific nvlist source-size limits.

## VFS Reference Helpers

- `zfs_vfs_ref(zfsvfs_t **zfvp)`
  - Returns `ESRCH` if the pointer is null.
  - Calls FreeBSD `vfs_busy()` to hold the mount.
  - On failure, clears `*zfvp` and returns `ESRCH`.
- `zfs_vfs_held(zfsvfs_t *zfsvfs)`
  - True when `z_vfs` is non-null.
- `zfs_vfs_rele(zfsvfs_t *zfsvfs)`
  - Releases the busy mount with `vfs_unbusy()`.

## Jail Ioctls

- `zfs_ioc_jail(zfs_cmd_t *zc)`
  - Attaches dataset `zc_name` to jail/zone id `zc_zoneid` using current thread credentials.
- `zfs_ioc_unjail(zfs_cmd_t *zc)`
  - Detaches dataset `zc_name` from jail/zone id `zc_zoneid`.

## FreeBSD Nextboot Ioctl

- Input keys are defined by `zfs_keys_nextboot`:
  - `"command"` string.
  - `ZPOOL_CONFIG_POOL_GUID`.
  - `ZPOOL_CONFIG_GUID`.
- `zfs_ioc_nextboot(...)`
  - Extracts pool guid, vdev guid, and command from input nvlist.
  - Resolves pool name through `spa_by_guid()` under `spa_namespace_enter()`.
  - Opens the spa, enters vdev state lock, looks up target vdev by guid, and writes the command to label pad2 with `vdev_label_write_pad2()`.
  - Waits for synced txg before closing the spa.

## Mount Cache Update

- `zfs_ioctl_update_mount_cache(const char *dsname)`
  - Finds mounted `zfsvfs` by dataset name.
  - Calls `VFS_STATFS()` to refresh `mp->mnt_stat`.
  - Releases the VFS reference.
  - Silently ignores lookup/statfs failures.

## Nvlist Limit

- `zfs_max_nvlist_src_size_os()`
  - Returns explicit `zfs_max_nvlist_src_size` if set.
  - Otherwise defaults to one quarter of `ptob(vm_page_max_user_wired)`.

## Initialization

- `zfs_ioctl_init_os()`
  - Registers:
    - `ZFS_IOC_JAIL`
    - `ZFS_IOC_UNJAIL`
    - named ioctl `"fbsd_nextboot"` for `ZFS_IOC_NEXTBOOT`
  - Uses config security policy and no pool checks for these registrations.

## External Dependencies

- FreeBSD VFS busy/unbusy APIs.
- FreeBSD jail dataset attach/detach helpers.
- SPA namespace and vdev label writing.
- VM page wiring limit for nvlist sizing.
