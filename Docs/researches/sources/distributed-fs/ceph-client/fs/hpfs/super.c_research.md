<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/super.c -->
# sources/distributed-fs/ceph-client/fs/hpfs/super.c

## Purpose

`sources/distributed-fs/ceph-client/fs/hpfs/super.c` implements HPFS filesystem registration, mount-context parsing, superblock validation, remount handling, dirty/clean shutdown marking, filesystem error policy, statfs, FITRIM ioctl support, and HPFS inode-cache allocation. It is the superblock and lifecycle entry point for the OS/2 HPFS driver, bridging Linux VFS `fs_context` and `super_operations` to HPFS on-disk boot/super/spare blocks.

## Important APIs, Types, and Functions

The VFS-facing objects are `hpfs_fs_type`, `hpfs_fc_context_ops`, and `hpfs_sops`. Entry points include `hpfs_init_fs_context()`, `hpfs_get_tree()`, `hpfs_fill_super()`, `hpfs_reconfigure()`, `hpfs_put_super()`, `hpfs_statfs()`, `hpfs_ioctl()`, module init/exit functions, and inode slab callbacks `hpfs_alloc_inode()` and `hpfs_free_inode()`.

Mount parsing uses `struct hpfs_fc_context`, `hpfs_param_spec`, and enum tables for `case=`, `check=`, `errors=`, `eas=`, and `chkdsk=`. Persistent-dirty helpers are `mark_dirty()` and `unmark_dirty()`. Error handling is centralized in exported `hpfs_error()`, while `hpfs_stop_cycles()` provides a lightweight cycle detector for other HPFS tree-walking code.

## Control Flow

Mount setup starts with `hpfs_init_fs_context()`, which allocates private context and installs defaults or, on reconfigure, copies current superblock options. `hpfs_parse_param()` fills that context. `hpfs_get_tree()` calls `get_tree_bdev()`, which invokes `hpfs_fill_super()` for block-device mounts.

`hpfs_fill_super()` allocates `struct hpfs_sb_info`, initializes the HPFS mutex, forces 512-byte blocks, maps sectors 0, 16, and 17, validates HPFS and spare-block magics, rejects unsupported writable versions, installs VFS superblock methods, imports HPFS geometry and mount options into `sbi`, loads hotfix, bitmap-directory, and codepage metadata, checks dirty shutdown and spare-dnode conditions, marks writable mounts dirty, validates directory-band geometry when checking is enabled, and finally reads the root inode with `iget_locked()`, `hpfs_init_inode()`, and `hpfs_read_inode()`. It then creates the root dentry and patches root inode timestamps and EA metadata from the root directory entry.

Remount uses `hpfs_reconfigure()`: it syncs the filesystem, rejects `timeshift` changes, clears prior dirty marking, updates option fields, and marks the volume dirty again for read-write operation. Unmount calls `hpfs_put_super()`, which unmarks dirty under the HPFS lock and frees `sbi` through RCU.

`hpfs_ioctl()` only handles `FITRIM`; it checks `CAP_SYS_ADMIN`, copies `struct fstrim_range`, converts byte ranges to 512-byte HPFS sectors, delegates to `hpfs_trim_fs()`, and returns the trimmed length in bytes.

## State and Persistence Behavior

Runtime state lives in `struct hpfs_sb_info`: geometry, bitmap directory, codepage table, free-space caches, dnode-map location, mount option values, error mode, time shift, and a prior-error flag. Free-sector and free-dnode counts are cached lazily by `hpfs_statfs()` and `hpfs_get_free_dnodes()` using bitmap scans.

Persistent state mutations are narrow but important. `mark_dirty()` writes sector 17 spare-block fields `dirty=1` and `old_wrote=0`; `unmark_dirty()` syncs the block device and writes clean or dirty-for-chkdsk state based on `chkdsk` policy and whether `hpfs_error()` was called. Writable mount setup also marks the spare block dirty. These writes are buffer-head based and synchronously flushed.

Error policy can change runtime mount state: `errors=panic` panics after marking dirty, `errors=remount-ro` sets `SB_RDONLY`, and `errors=continue` leaves a writable corrupted filesystem running while recording `sb_was_error`.

## Dependencies and Integration Points

The file depends on HPFS helpers declared in `hpfs_fn.h` for sector mapping, bitmap prefetch, bitmap-directory/codepage loading, hotfix maps, inode initialization, root fnode lookup, directory entry mapping, filesystem checks, and trimming. VFS integration is through block-device mounts, `fs_context`, `super_operations`, dentry operations, inode cache slabs, `statfs`, and Linux user-copy/capability helpers.

On-disk integration centers on HPFS boot, super, and spare blocks and little-endian conversions. Test and runtime observability is mostly through `pr_err()`, `pr_info()`, mount errors, dirty flags visible to OS/2 chkdsk, and statfs output.

## Risks and Edge Cases

Mount-time validation is safety-critical because HPFS structures are consumed by later inode and directory walkers. Disabling checks (`check=none`) reduces corruption defenses. Dirty shutdown handling, spare-dnode usage, and version rejection are tied to whether the mount is writable and to `errors=` behavior.

The bailout path must release mapped buffer heads in the right order and free `sbi` exactly once. `hpfs_put_super()` uses RCU freeing for `sbi`, so readers must access it through normal superblock lifetime rules. `timeshift` is intentionally immutable across remount because timestamps are interpreted through that offset.

`FITRIM` range conversion rounds by shifting to 512-byte sectors; boundary behavior depends on `hpfs_trim_fs()` interpreting `[start,end)` consistently. Error handling can set `SB_RDONLY` directly, so any path that assumes normal remount sequencing should be careful.

## Test Signals

Useful tests include mounting valid and invalid HPFS images, bad magic/version images, dirty-spare-block images, spare-dnode-used images, and images with inconsistent directory-band geometry under each `check=` and `errors=` mode. Remount tests should verify option persistence, readonly/readwrite transitions, and rejection of changed `timeshift`.

Operational signals include spare-block dirty/old_wrote transitions across mount/unmount/error, `statfs` free counts matching HPFS bitmaps, root inode timestamp import, FITRIM permission and range behavior, inode slab init/teardown under module load/unload, and absence of leaked buffer heads on mount failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hpfs/super.c -->
