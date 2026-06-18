# sources/distributed-fs/ceph-client/fs/afs/dir.c

Purpose: `dir.c` is the main VFS-facing directory implementation for the AFS client. It wires directory file, inode, address-space, and dentry operations, and implements lookup, readdir, dentry revalidation, create, mkdir, rmdir, unlink, link, symlink, rename, and single-blob cache writeback for directory and symlink data.

Important APIs and functions: exported operation tables are `afs_dir_file_operations`, `afs_dir_inode_operations`, `afs_dir_aops`, and `afs_fs_dentry_operations`. Key read paths are `afs_dir_open()`, `afs_read_single()`, `afs_read_dir()`, `afs_dir_iterate()`, `afs_readdir()`, `afs_do_lookup_one()`, and `afs_do_lookup()`. Mutation entry points are `afs_create()`, `afs_mkdir()`, `afs_rmdir()`, `afs_unlink()`, `afs_link()`, `afs_symlink()`, and `afs_rename()`.

Control flow: directory reads call `afs_read_dir()`, which coordinates `validate_lock`, synchronously downloads invalid directory data with netfs, verifies AFS directory blocks, and keeps a read lock for iteration. Lookup validates the parent, supports `@sys` substitution, searches through `afs_dir_search()`, optionally uses InlineBulkStatus for lookup-ahead, and splices or instantiates the inode. Mutations allocate `struct afs_operation`, set expected data-version deltas, execute the AFS/YFS RPC, commit returned statuses, and locally edit cached directory data only when server version movement matches expectations.

State and persistence: dentry `d_fsdata` stores the parent directory data version observed at lookup time. Directory contents live in `vnode->directory` folio queues and can be written as a single fscache blob by `afs_single_writepages()`. Important flags include `AFS_VNODE_DIR_VALID`, `AFS_VNODE_DIR_READ`, `AFS_VNODE_DELETED`, `AFS_VNODE_NEW_CONTENT`, and `DCACHE_NFSFS_RENAMED`.

Dependencies and integration points: this file integrates VFS operations with `dir_search.c`, `dir_edit.c`, `dir_silly.c`, `inode.c`, `fs_operation.c`, `fsclient.c`, YFS RPCs, fscache/netfs, callback validation, and Linux dcache locking.

Risks: cache correctness depends on data-version comparisons and invalidation. Rename and unlink paths contain subtle dcache races around `d_drop()`, `d_rehash()`, `d_move()`, silly rename, and `d_fsdata` refresh. Readdir/lookup retry loops must avoid spinning on repeated `-ESTALE`.

Test signals: malformed directory blobs, lookup with stale dentry versions, `@sys`, create/mkdir/symlink/link edits, unlink/rmdir/sillyrename, rename replace/noreplace/exchange/cross-directory moves, RCU and non-RCU dentry revalidation, and single-blob fscache writeback.
