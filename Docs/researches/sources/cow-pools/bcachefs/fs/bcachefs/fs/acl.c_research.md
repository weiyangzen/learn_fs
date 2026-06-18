# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/acl.c

Implements POSIX ACL serialization/deserialization, VFS get/set ACL hooks, ACL xattr updates, and chmod ACL adjustment.

Key entry points:
- `bch2_acl_to_text()` formats on-disk ACL xattr payloads for diagnostics.
- `bch2_get_acl()` looks up ACL xattrs, converts them to `struct posix_acl`, and caches them on the VFS inode.
- `bch2_set_acl_trans()` sets or deletes ACL xattrs in a btree transaction.
- `bch2_set_acl()` is the VFS-facing setter with inode update locking and transaction retry handling.
- `bch2_acl_chmod()` updates an access ACL after mode changes.

Core mechanics:
- On-disk ACLs start with `bch_acl_header` version `BCH_ACL_VERSION`, followed by short entries for owner/group/mask/other and long entries for named user/group.
- `bch2_acl_from_disk()` validates size, version, tags, and entry boundaries before allocating a POSIX ACL.
- `bch2_acl_to_xattr()` counts short/long entries, allocates a bcachefs xattr key, writes little-endian ACL entries, and rejects oversized values.
- ACLs are stored as xattrs using `KEY_TYPE_XATTR_INDEX_POSIX_ACL_ACCESS` or `KEY_TYPE_XATTR_INDEX_POSIX_ACL_DEFAULT`.
- Default ACLs are accepted only for directories; clearing a default ACL on a non-directory is a no-op.
- Access ACL set calls `posix_acl_update_mode()` and writes the updated mode/ctime back to the inode.

Important invariants:
- ACL xattr values must use the exact version and entry layout expected by the parser.
- `bch2_acl_from_disk()` may allocate while dropping transaction locks.
- Inode mode/ctime and ACL xattr updates are committed atomically in `__bch2_set_acl()`.
- Cached VFS ACLs are updated after successful commit.

Filesystem relevance:
- Provides bcachefs support for POSIX ACL permissions through the filesystem xattr btree and VFS ACL interface.

Notable risks:
- Malformed ACL xattrs return errors and print diagnostic messages.
- UID/GID conversion uses `init_user_ns`.
- Chmod ACL updates depend on the existing access ACL xattr being found and rewritten at the current hash position.
