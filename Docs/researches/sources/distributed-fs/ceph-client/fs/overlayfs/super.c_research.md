# sources/distributed-fs/ceph-client/fs/overlayfs/super.c

## Purpose
`super.c` registers the OverlayFS filesystem type and builds an overlay superblock from a parsed fs context. It probes upper/work/lower capabilities, creates work/index directories, assigns fsids and xino policy, checks overlapping layers, initializes root inode/dentry state, and defines superblock/dentry/inode operations.

## Important APIs, types, and functions
Key operations are `ovl_fill_super()`, `ovl_fill_super_creds()`, `ovl_get_upper()`, `ovl_get_workdir()`, `ovl_make_workdir()`, `ovl_get_indexdir()`, `ovl_get_layers()`, `ovl_get_lowerstack()`, `ovl_get_root()`, `ovl_check_overlapping_layers()`, `ovl_sync_fs()`, `ovl_statfs()`, and module init/exit registration. Dentry ops implement `d_real`, strong/weak revalidation, and optional case-insensitive hash/compare. Inode ops allocate, free, destroy, and clean per-inode OverlayFS state.

## Control flow
`ovl_fill_super()` verifies the caller user namespace, sets dentry operations, prepares creator credentials if needed, then runs `ovl_fill_super_creds()` under override creds. The fill path verifies parsed options, allocates layers and lowerdir strings, initializes xino assumptions, sets super operations early for trap inode support, processes upper/workdir if present, builds the lower stack, initializes persistent UUID when requested, creates/validates the index directory if enabled, checks layer overlap, selects export operations, lowers `CAP_SYS_RESOURCE`, sets superblock flags, and builds the root dentry.

Workdir creation probes upper features: directory creation/cleanup, `d_type`, `O_TMPFILE`, `RENAME_WHITEOUT`, OverlayFS xattr support, volatile dirty marker creation, file-handle decode, and NFS-export dependency on index. Missing optional features downgrade config or force read-only; missing required remote-upper features fail the mount.

## State and persistence
Persistent state includes work/index directories under workdir, `work/incompat/volatile/dirty`, index xattrs linking upper root to indexdir, upper root UUID xattr, and root origin verification. In-memory state includes layer cloned mounts, pseudo devices per unique fs, trap inodes, in-use locks, root `ovl_entry`, root flags, export operations, and inode cache objects.

## Dependencies and integration points
It integrates with `params.c` for config and context, `namei.c` for origin/index validation, `readdir.c` for `d_type` and cleanup, `util.c` for xattrs/sync/in-use, and VFS mount/fs_context infrastructure. It registers `ovl_fs_type` with `FS_USERNS_MOUNT` and `kill_anon_super`.

## Risks
Feature downgrades are subtle: xattr/file-handle/d_type/whiteout limitations must not leave config inconsistent. Workdir/index cleanup has persistent data risk. Overlap detection must prevent recursive layer exposure. Volatile mounts must refuse unseen upper writeback errors. Reference ownership during partial mount failures is complex.

## Test signals
Test upperless and upperful mounts, missing workdir, read-only upper, same versus separate upper/work mount, unsupported upper xattrs, remote upper rejection, volatile dirty markers and sync behavior, index creation/cleanup, root origin verification, xino mode decisions, lower UUID conflicts, casefold encoding, export modes, overlap/in-use detection, and unmount cleanup.
