# sources/distributed-fs/ceph-client/fs/hfs/hfs_fs.h

Purpose: central private header for classic HFS. It defines HFS-specific inode and superblock state, dirty flags, helper macros, timestamp conversions, the 512-byte read macro, and cross-file function prototypes.

Important types and APIs: `struct hfs_inode_info` extends VFS inodes with open count, flags, catalog key, resource-fork inode linkage, extent lock, first/cached extents, allocation/physical sizes, and open-directory cursor list. `struct hfs_sb_info` stores MDB buffers, primary/alternate MDB pointers, in-memory volume bitmap, catalog/extents trees, atomic file/folder/CNID counters, allocation geometry, mount options, NLS tables, bitmap lock, delayed MDB work, and dirty flags. Mac/Unix timestamp conversion helpers apply the HFS 1904 epoch and system timezone behavior. `HFS_I()` and `HFS_SB()` are the main accessors used throughout the filesystem.

State and persistence: header fields mirror the MDB, volume bitmap, catalog records, extent records, and btree fork metadata. Dirty flags `HFS_FLG_BITMAP_DIRTY`, `HFS_FLG_MDB_DIRTY`, and `HFS_FLG_ALT_MDB_DIRTY` coordinate delayed and sync-time persistence. Inode flags track resource forks and cached overflow extents.

Dependencies and integration: includes Linux VFS, buffer, mutex, workqueue, endian, and uaccess headers plus `hfs.h`. It declares APIs from bitmap, catalog, extent, inode, MDB, partition, string, translation, xattr, and super modules.

Risks and test signals: this header encodes global invariants: counter widths must stay within `u32`, allocation block geometry must match MDB values, and timestamp conversions depend on global timezone. Tests should exercise remount/sync dirty flags, timezone dentry revalidation, resource forks, and special CNID inodes.
