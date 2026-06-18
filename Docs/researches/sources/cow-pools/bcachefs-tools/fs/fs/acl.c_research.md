# File Research: sources/cow-pools/bcachefs-tools/fs/fs/acl.c

## Purpose

Implements bcachefs POSIX ACL encoding, decoding, xattr conversion, VFS get/set hooks, and chmod ACL updates.

## Main Interfaces

- `bch2_acl_to_text()` prints on-disk ACL xattr values.
- Under `!NO_BCACHEFS_FS`:
  - `bch2_get_acl()`.
  - `bch2_set_acl_trans()`.
  - `bch2_set_acl()`.
  - `bch2_acl_chmod()`.

## Behavior

On-disk ACLs begin with `bch_acl_header` version `BCH_ACL_VERSION`, then short or long entries. Short entries are used for object/mask/other tags; long entries include UID/GID for user/group entries.

`bch2_acl_from_disk()` validates version, size, entry tags, and entry boundaries, counts entries, allocates a Linux `posix_acl`, and converts little-endian ids/perms to kernel IDs. `bch2_acl_to_xattr()` performs the reverse conversion into a `KEY_TYPE_XATTR_INDEX_POSIX_ACL_*` xattr key.

`bch2_get_acl()` hashes and looks up the ACL xattr, converts it, caches it in the VFS inode, and returns NULL on ENOENT. Set paths reject default ACLs on non-directories, use hash set/delete for ACL xattrs, update mode for access ACLs, write inode ctime/mode changes, commit, update the in-memory inode, and refresh cached ACLs. `bch2_acl_chmod()` loads an access ACL, applies `__posix_acl_chmod()`, and updates the xattr.

## State And Side Effects

ACL changes modify xattr btrees and inode metadata. VFS-facing paths take `ei_update_lock`, use btree transactions, and update cached ACLs.

## Dependencies

Uses xattr hashing, inode operations, bcachefs transactions, VFS inode wrappers, Linux POSIX ACL APIs, and allocation helpers that can drop btree locks.

## Risks And Notes

Malformed on-disk ACLs return `-EINVAL`. Allocation failures use the custom `ENOMEM_acl` error. The `NO_BCACHEFS_FS` build excludes VFS functions and leaves transaction helpers stubbed in the header.
