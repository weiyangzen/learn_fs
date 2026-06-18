# File Research: sources/block-storage/lvm2/lib/device/filesystem.c

## Purpose
Implements filesystem discovery and helper-script orchestration for `lvresize --resizefs` style operations, including mounted filesystem detection, btrfs multi-device handling, LUKS/dm-crypt layers, and mounted-LV rename safety checks.

## Main Responsibilities
- Resolves the lvresize filesystem helper path from `LVRESIZE_FS_HELPER_PATH` or `global/lvresize_fs_helper_executable`.
- Finds dm-crypt holder devices above an LV by scanning `/sys/dev/block/<lv>/holders`.
- Reports whether an LV has an active crypt holder through `lv_crypt_is_active`.
- Finds mount points for normal filesystems through `/etc/mtab`, matching either mount directory `st_dev` or btrfs device `st_rdev`.
- Handles mounted btrfs by walking `/sys/fs/btrfs/<uuid>/devices` and matching each device to the LV dev_t.
- Populates `struct fs_info` with blkid data, mount state, filesystem path, crypt-layer metadata, and XFS mounted geometry corrections.
- Detects unsafe mount-state/name mismatches after LV rename by comparing `/etc/mtab`, `/proc/mounts`, `/dev/mapper/<vg-lv>`, and resolved realpaths.
- Invokes the helper executable for crypt resize, filesystem reduce, and filesystem extend operations.

## Important Control Flow
`fs_get_info` builds the LV path, stats it, gets initial blkid info, and returns `nofs` if no filesystem exists. If the LV contains `crypto_LUKS`, it locates the active crypt holder, opens it, reads its size, probes filesystem info from the crypt device, marks `needs_crypt`, records crypt dev_t and data offset, and treats the crypt device as the filesystem device.

Mounted btrfs cannot be matched only via mount directory `st_dev`, so `_btrfs_get_mnt` uses btrfs sysfs devices and then calls `_fs_get_mnt` to find the shared mount point. Mounted XFS updates `fs_last_byte` using `fs_xfs_update_size_mounted` because blkid's `FSLASTBLOCK` can be wrong for mounted XFS.

`fs_reduce_script` and `fs_extend_script` construct argv arrays for `lvresize_fs_helper`, adding flags for fstype, LV path, new size, mount dir, unmount/mount/fsck/remount requirements, and optional crypt resize. They do not perform filesystem-specific operations directly.

## Dependencies
Depends on blkid wrappers from `dev-type.c`, `struct fs_info` from `filesystem.h`, device-mapper path helpers, crypt table offset helper, mount table APIs, sysfs paths, and `exec_cmd`.

## Risk Notes
- Crypt holder detection assumes a single relevant `dm-*` holder and does not verify the holder DM UUID as crypt.
- LV rename detection is conservative; inconsistencies between mtab/proc paths abort resizing to avoid filesystem utility failures.
- Helper argv capacity is fixed by `FS_CMD_MAX_ARGS`; adding flags requires preserving bounds.
- btrfs multi-device matching treats one mount entry as shared across devices and requires both device presence and mount point discovery.
