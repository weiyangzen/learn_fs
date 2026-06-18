# sources/distributed-fs/ceph-client/fs/ntfs/ea.c

Purpose: implements NTFS extended attributes, Linux xattr handlers, WSL metadata EAs, DOS/NTFS attribute xattrs, and optional POSIX ACL storage.

Important APIs and functions:
- `ntfs_get_ea()` reads a named EA from `$EA_INFORMATION` plus `$EA`.
- `ntfs_set_ea()` creates, replaces, removes, and rewrites EA entries while maintaining packed EA size, query length, and `NEED_EA` counts.
- `ntfs_ea_get_wsl_inode()` and `ntfs_ea_set_wsl_inode()` map `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` EAs to Linux uid/gid/mode/device state.
- `ntfs_listxattr()` lists EA names for VFS xattr enumeration.
- `ntfs_getxattr()` and `ntfs_setxattr()` implement generic xattr handlers including `system.dos_attrib`, `system.ntfs_attrib`, and `system.ntfs_attrib_be`.
- `ntfs_new_attr_flags()` changes sparse/compressed attribute flags for empty regular files by resizing the attribute record layout.
- Optional ACL functions store POSIX ACL xattrs in NTFS EAs and update WSL mode metadata.

Control flow:
- EA lookup iterates packed `struct ea_attr` records using `next_entry_offset`, validates record size/name/value bounds, and returns offset plus effective size.
- `ntfs_get_ea()` validates `NInoHasEA`, reads `$EA_INFORMATION`, bounds `ea_query_length` against `$EA`, and copies or sizes the value.
- `ntfs_set_ea()` creates `$EA_INFORMATION` when missing, removes or replaces an existing entry, writes updated metadata first, writes/truncates `$EA`, then appends the new aligned EA record if a value remains.
- DOS/NTFS xattr set operations update `ni->flags`, adjust write permissions from `FILE_ATTR_READONLY`, mark filename metadata dirty, and dirty the inode.
- ACL set converts ACLs to xattr blobs, writes/removes them as EAs, updates `i_mode` and `$LXMOD`, and rolls back the ACL xattr on WSL mode write failure.

State and persistence behavior:
- Writes use `ntfs_write_ea()`, which opens a fake attribute inode, calls `ntfs_inode_attr_pwrite()`, optionally truncates trailing old EA bytes, and marks the base MFT record dirty.
- `NInoHasEA` is updated based on remaining EA query size.
- Attribute flag changes mutate both on-disk `attr_record.flags` and in-memory NTFS inode flags/compression fields.
- xattr and ACL setters update ctime and call `mark_inode_dirty()`.
- WSL EA getters can overwrite Linux inode uid/gid/mode during inode load unless mount options already supplied uid/gid.

Dependencies and integration points:
- Depends on `layout.h`, `attrib.h`, `index.h`, `dir.h`, and `ea.h`.
- Uses inode attribute read/write helpers from `inode.c`.
- Integrates with VFS xattr and POSIX ACL APIs through `ntfs_xattr_handlers` and inode operation tables in `file.c`.
- Sparse/compressed flag changes depend on mapping pair sizing and `ntfs_attr_record_resize()`.

Risks and edge cases:
- `ntfs_set_ea()` writes `$EA_INFORMATION` before `$EA` in some removal paths; later failure can leave metadata inconsistent despite comments promising restore.
- Setting a generic xattr with `value == NULL` and nonzero size would be unsafe, though VFS normally controls this.
- `ntfs_new_attr_flags()` returns early when flags do not change without releasing the search context or unmapping the MFT record, which appears to leak resources.
- `ntfs_setxattr()` always updates ctime and dirties the inode even on failed set operations.
- EA list parsing trusts `ea_query_length` after top-level bounds and must reject malformed `next_entry_offset` loops.

Test signals:
- xattr tests should cover create/replace/remove, ERANGE sizing, malformed EA records, DOS/NTFS endian attributes, read-only bit mode interaction, and empty-EA cleanup.
- WSL tests should verify uid/gid/mode/device round trips and mount-option override behavior.
- ACL tests should cover default ACL rejection on non-directories, symlink rejection, chmod ACL update, and rollback on `$LXMOD` write failure.
