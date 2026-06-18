<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/namei.c -->
## sources/distributed-fs/ceph-client/fs/ntfs3/namei.c

Purpose: provides NTFS3 VFS directory and dentry operations: lookup, create, mknod, link, unlink, symlink, mkdir, rmdir, rename, parent lookup, and case-insensitive dentry hashing/comparison.

Important APIs and functions: exported/registered functions include `fill_name_de`, `ntfs_lookup`, `ntfs_create`, `ntfs_mknod`, `ntfs_link`, `ntfs_unlink`, `ntfs_symlink`, `ntfs_mkdir`, `ntfs_rmdir`, `ntfs_rename`, `ntfs3_get_parent`, `ntfs_d_hash`, and `ntfs_d_compare`. The file defines `ntfs_dir_inode_operations`, `ntfs_special_inode_operations`, and `ntfs_dentry_ops`.

Control flow: lookup converts the VFS name to UTF-16, locks the directory, searches the NTFS directory index, rejects malformed non-base inodes without inode operations, and splices aliases. Create/mknod/symlink/mkdir call `ntfs_create_inode` with the appropriate mode and payload. Link checks directory and link-count constraints, locks parent and target, increments VFS links before `ntfs_link_inode`, and rolls back on failure. Unlink/rmdir lock the directory and call `ntfs_unlink_inode`. Rename rejects unsupported flags and metadata files, unlinks an existing target if present, builds old and new directory entries, locks old dir, inode, and optionally new dir, calls `ni_rename`, then updates timestamps and synchronous-write behavior. Dentry hash/compare use ASCII uppercase fast paths and UTF-16/upcase-table slow paths.

State and persistence behavior: persistent changes are delegated to inode/index helpers that mutate MFT records and directory indexes. This file updates VFS link counts, timestamps, dirty inode state, and dentry instantiation. `fill_name_de` constructs an in-memory `NTFS_DE` containing an `ATTR_FILE_NAME` key for later index insertion/removal.

Dependencies and integration points: depends on NLS conversion, NTFS name collation/upcase tables, inode creation/link/unlink/rename helpers, directory search, ACL/xattr/getattr/setattr/fiemap operations, and VFS dentry/inode operation registration.

Risks: locking order across old directory, target inode, and new directory is important for rename/link correctness. Rename unlinks an existing target before inserting the moved name, so rollback behavior depends on lower helpers. Case-insensitive hashing must match comparison and NTFS collation or dentries can alias incorrectly. UTF-16 conversion failures and `PATH_MAX` scratch buffers limit long names.

Test signals: case-insensitive lookup/hash/compare with ASCII and non-ASCII names, create/mkdir/mknod/symlink and later lookup, hardlink link-count limits, unlink and rmdir on bad/forced-shutdown states, rename same-name no-op, cross-directory rename, rename over existing target, metadata-file rename rejection, parent lookup via `ATTR_NAME`, and Windows-name/NLS edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs3/namei.c -->
