# sources/distributed-fs/ceph-client/fs/hfs/inode.c

Purpose: implements classic HFS inode lifecycle, file address-space operations, fork metadata import/export, inode writeback to catalog records, resource-fork pseudo-directory lookup, file open/release, setattr, and fsync.

Important APIs and control flow: `hfs_aops` and `hfs_btree_aops` wire page cache operations to `hfs_get_block()`, with btree folio release checking cached bnode references. `hfs_write_begin()` uses `cont_write_begin()` and truncates failed extension writes. `hfs_new_inode()` allocates CNIDs, initializes mode/owner/timestamps, updates file/folder/root counts, and marks MDB dirty. `hfs_delete_inode()` decrements counters and truncates unlinked regular files. `hfs_inode_read_fork()` and `hfs_inode_write_fork()` translate catalog/MDB fork fields into in-memory extent state and back. `hfs_iget()` uses `iget5_locked()` with catalog records. `hfs_write_inode()` flushes dirty extents, special btree headers, or catalog file/folder records. `hfs_file_lookup()` exposes a file's resource fork under a synthetic `rsrc` child. `hfs_inode_setattr()` restricts uid/gid/mode changes to HFS-supported semantics and truncates on size changes. `hfs_file_fsync()` writes inode/catalog state, flushes delayed MDB work, then syncs the block device.

State and persistence: inode writeback updates catalog records for times, directory valence, file lock bit, and fork extents/sizes. Special extents/catalog btree inodes update btree headers. Resource-fork inodes share the main catalog record and hold cross references.

Dependencies and integration: integrates VFS address-space/file/inode operations with `extent.c`, `catalog.c`, `mdb.c`, `super.c`, and xattr listing. It depends on Linux page cache, direct I/O, mpage writeback, and credential APIs.

Risks and test signals: resource fork handling uses fake hashed inodes and shared catalog state. Counter updates occur before catalog insertion can fail, relying on cleanup paths. Tests should cover resource fork reads/writes, direct I/O extension failure, writeback of btree inodes, mode mapping, truncate-on-last-close, and fsync persistence.
