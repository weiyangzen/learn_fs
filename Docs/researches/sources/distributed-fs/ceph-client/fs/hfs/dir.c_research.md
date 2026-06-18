# sources/distributed-fs/ceph-client/fs/hfs/dir.c

Purpose: provides VFS directory operations for classic HFS: lookup, iteration, create, mkdir, unlink/rmdir, rename, and release cleanup for active directory reads.

Important APIs and control flow: `hfs_lookup()` searches the catalog by parent/name and instantiates the inode with `hfs_iget()`. `hfs_readdir()` emits synthetic `.` and `..`, then walks catalog leaf records using `hfs_brec_goto()`, converts Mac names to Linux names, emits directory/file entries, and saves the last key in `file->private_data` when the caller stops mid-stream. `hfs_dir_release()` removes that saved readdir state. `hfs_create()` and `hfs_mkdir()` allocate a new inode and insert catalog records, cleaning up the inode on failure. `hfs_remove()` handles both unlink and rmdir, rejects nonempty directories, validates CNID counters, deletes catalog records, clears nlink, and invokes inode deletion. `hfs_rename()` implements only normal and `RENAME_NOREPLACE`, removes an existing destination first, then calls `hfs_cat_move()`.

State and persistence: directory size is catalog valence plus synthetic entries. New and removed entries update catalog tree pages, inode link counts, inode timestamps, and MDB counters via inode/catalog helpers. Active readdir cursors are linked in `HFS_I(dir)->open_dir_list` and adjusted during deletion to avoid skipped or duplicated entries.

Dependencies and integration: integrates VFS `file_operations`/`inode_operations` with `catalog.c`, `inode.c`, `string.c`, and `trans.c`. Dentry hashing/comparison is installed by `super.c`.

Risks and test signals: destination removal before rename means failures after removal are visible to users. Directory iteration trusts catalog ordering and parent checks to detect corruption. Tests should cover interrupted readdir with concurrent unlink, nonempty rmdir, rename replacement, oversized names, and CNID count read-only/corruption paths.
