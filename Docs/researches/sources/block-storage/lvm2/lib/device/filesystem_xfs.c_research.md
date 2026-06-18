# File Research: sources/block-storage/lvm2/lib/device/filesystem_xfs.c

## Purpose
Provides the mounted-XFS size correction used by `filesystem.c` when blkid may report inaccurate `FSLASTBLOCK` for mounted XFS filesystems.

## Main Behavior
`fs_xfs_update_size_mounted` opens the XFS mount directory, issues `XFS_IOC_FSGEOMETRY`, and replaces `fsi->fs_last_byte` with `geo.blocksize * geo.datablocks`.

## Portability Handling
If `<xfs/xfs.h>` is available, the file uses the system XFS definitions. Otherwise, it defines the ioctl number and a minimal compatible `struct xfs_fsop_geom` containing the fields needed by LVM.

## Dependencies
Depends on `filesystem.h`, LVM logging, `open`, `ioctl`, and `close`.

## Risk Notes
The fallback struct assumes stable basic XFS geometry layout. Failure to open or query the mount directory leaves XFS size correction unavailable and causes `fs_get_info` to fail for the mounted-XFS correction path.
