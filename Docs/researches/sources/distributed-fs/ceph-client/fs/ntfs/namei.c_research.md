# sources/distributed-fs/ceph-client/fs/ntfs/namei.c

## Purpose
`namei.c` implements NTFS directory inode operations and export support: lookup, create, mkdir, unlink, rmdir, rename, symlink, mknod, hard-link creation, parent lookup, and file-handle decoding. It bridges VFS namespace requests to NTFS Unicode names, file-name attributes, directory indexes, MFT records, security descriptors, EA metadata, and reparse points.

## Important APIs and Functions
The file defines `ntfs_dir_inode_ops` and `ntfs_export_ops`. Core helpers are `ntfs_check_bad_windows_name()`, `ntfs_lookup()`, `ntfs_sd_add_everyone()`, `__ntfs_create()`, `ntfs_delete()`, `__ntfs_link()`, `ntfs_rename()`, and `ntfs_get_parent()`. Public-facing VFS callbacks wrap these helpers: `ntfs_create()`, `ntfs_unlink()`, `ntfs_mkdir()`, `ntfs_rmdir()`, `ntfs_symlink()`, `ntfs_mknod()`, and `ntfs_link()`.

## Control Flow and State
Name handling converts dentry bytes through `ntfs_nlstoucs()` and rejects illegal Windows characters, reserved device names, and optional trailing dot/space cases. Lookup searches directory indexes under `mrec_lock`, handles exact POSIX/WIN32 matches, case-insensitive aliases through `d_add_ci()`, and DOS-name redirection to the corresponding WIN32 name.

`__ntfs_create()` allocates a new VFS inode, initializes NTFS inode state, applies masks/ownership/ACLs, marks parent timestamps, allocates an MFT record, inserts the inode hash as `I_NEW | I_CREATING`, and then under child/parent MFT locks creates standard information, a permissive security descriptor, either index-root or data attributes, WSL reparse data for symlinks/special files, WSL EA metadata, a POSIX `FILE_NAME` attribute, and the parent directory index entry. It sets link count, VFS operations, and instantiates through callers. Error paths remove created attributes, delete reparse index entries, free extent/base MFT records, remove the inode hash, and discard the new inode.

Deletion finds matching `FILE_NAME` attributes by namespace and case rules, checks directory emptiness/hard-link exceptions, removes the directory index entry and attribute, decrements link counts, and when the MFT link count reaches zero marks the inode being deleted and removes reparse/object-id indexes. Rename is implemented as delete target if present, link old inode into the new directory/name, then delete the old name, with rollback by deleting the newly added link if old-name deletion fails.

## Dependencies and Integration
This file integrates with `mft`, `index`, `reparse`, `object_id`, `ea`, ACL, time conversion, Unicode collation, VFS inode/dentry APIs, and NFS export helpers. It marks the NTFS volume dirty before mutating namespace state.

## Risks
Namespace mutation ordering is corruption-sensitive: adding an index entry before an attribute or failing rollback can leave dangling names. Rename is not an atomic metadata transaction. `ntfs_link()` does not call `ntfs_check_bad_windows_name()` unlike create/unlink/mkdir/rename. Several error paths map to `-ENOMEM` for conversion failures even if the underlying error differs. The permissive security descriptor may be policy-sensitive.

## Test Signals
Test exact/case-insensitive/DOS-name lookups, reserved names, hidden dot files, create/mkdir/symlink/mknod with rollback fault injection, hard links across directories, unlink of files with object IDs/reparse points, non-empty directory unlink rules, rename overwrite and cross-directory rename, NFS export parent lookup, and concurrent create/delete writeback interactions involving `I_CREATING` and `NInoBeingDeleted`.
