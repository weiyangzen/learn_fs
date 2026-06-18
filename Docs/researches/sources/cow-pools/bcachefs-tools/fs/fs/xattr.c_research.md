# File Research: sources/cow-pools/bcachefs-tools/fs/fs/xattr.c

## Purpose
Implements bcachefs extended attribute storage, lookup, validation, VFS xattr handlers, xattr listing, POSIX ACL value printing, and synthetic `bcachefs.*` / `bcachefs_effective.*` xattrs for inode options.

## Main Contents
- Xattr hash descriptor implementation:
  - Hash includes xattr type byte plus name.
  - Key and bkey comparison check type, name length, and name bytes.
  - `bch2_xattr_hash_desc` targets `BTREE_ID_xattrs` with `KEY_TYPE_xattr`.
- `bch2_xattr_validate()`, checking value size bounds, known type, and absence of NUL bytes in names.
- `bch2_xattr_to_text()`, which prints namespace prefix, name, value, and ACL text for POSIX ACL xattrs.
- `bch2_xattr_get_trans()`, a transaction-level lookup using inode hash info and `bch2_hash_lookup()`.
- `bch2_xattr_set()`, the exported transaction-level setter/delete path. It checks subvolume writability, peeks and updates inode ctime, writes the inode to ensure snapshot presence, then inserts/replaces/deletes the xattr through the generic string hash layer.
- Listing helpers:
  - `__bch2_xattr_emit()` emits prefix+name NUL-terminated list entries.
  - `bch2_xattr_emit()` respects handler list permissions.
  - `bch2_xattr_list_bcachefs()` lists defined and effective inode options.
  - `bch2_xattr_list()` walks the xattr btree for an inode and appends synthetic bcachefs option names.
- VFS handlers for user, trusted, security, bcachefs, and bcachefs_effective namespaces.
- `bcachefs.*` option get/set code maps option names to inode option ids, parses option values, runs option hooks, updates project id/casefold/31-bit dirent flags, writes the inode under update lock, and notifies directory casefold changes.
- Type-to-handler map includes POSIX ACL access/default nop handlers for stored ACL xattrs.

## Integration Notes
Stored xattrs are hashed by inode hash info and live in `BTREE_ID_xattrs`. Synthetic bcachefs option xattrs operate directly on inode fields rather than xattr btree keys. ACL code stores ACLs through this same xattr format. The xattr setter deliberately writes the inode ctime in the same transaction so snapshot-visible xattrs have a matching inode key.

## Risks and Edge Cases
- Validation allows a value size up to `xattr_val_u64s(name_len, val_len + 4)` with an in-code "XXX why +4 ?" note.
- `Inode_opt_inodes_32bit` can only be changed after confirming the directory is empty, because existing dirents would otherwise require rehashing.
- `bcachefs_effective.*` set is a no-op because effective values are inherited.
- Trusted xattrs list only for callers with `CAP_SYS_ADMIN`.
