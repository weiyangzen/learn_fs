# sources/distributed-fs/ceph-client/fs/ntfs3/ntfs_fs.h

## Purpose
`ntfs_fs.h` is the NTFS3 in-memory subsystem interface. It defines mount options, superblock state, inode extensions, runlist containers, bitmap/index state, locks, feature flags, and cross-file function prototypes.

## Important APIs, Types, and Constants
`ntfs_mount_options` captures uid/gid, masks, charset, ACLs, discard, sparse, metadata visibility, Windows-name enforcement, case sensitivity, preallocation, and delayed allocation. `runs_tree` stores decoded extents. `wnd_bitmap` models free-space bitmaps and extent hints. `ntfs_index` tracks index allocation and bitmap runs. `ntfs_sb_info` is the mounted-volume state for geometry, MFT, allocation bitmap, volume info, `$Secure`, `$Reparse`, `$ObjId`, compression contexts, mount options, ratelimits, and procfs. `mft_inode` wraps one MFT record; `ntfs_inode` embeds the Linux inode and adds NTFS records, runs, indexes, attribute lists, flags, and locks.

## Control Flow and Integration
Mount initializes `ntfs_sb_info`; inode load initializes `ntfs_inode`; file and attribute operations mutate `runs_tree` under locks; sync and teardown walk this state to flush metadata and release references. The header declares APIs from NTFS3 attribute, bitmap, directory, file, record, run, super, upcase, xattr, and compression modules.

## State and Persistence Behavior
The structures bridge disk metadata with VFS state. Cached upcase tables, attribute definitions, free-space bitmaps, delayed allocation counters, dirty MFT records, file run caches, and index state all live here. Time helpers preserve NTFS 100 ns timestamp semantics.

## Dependencies and Integration Points
It depends on Linux VFS, buffer-head, memory-management, rbtree, rwsem, uid/gid, folio, and block APIs, and includes `ntfs.h`. POSIX ACL exports are conditional on `CONFIG_NTFS3_FS_POSIX_ACL`.

## Risks
Lock ordering, stale run caches, delayed-allocation accounting drift, dirty propagation, and 32/64-bit cluster differences are the main risks. Inline helpers spread caller assumptions across the filesystem.

## Test Signals
Compile ACL, compression, and 64-bit cluster variants. Exercise mount/remount, statfs with delayed allocation, sparse/compressed max-size checks, directory rename locks, teardown, and dirty inode writeback.
