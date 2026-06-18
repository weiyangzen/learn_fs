# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr.c

This file implements bcachefs extended attributes, using `str_hash` for xattr btree keys and Linux xattr handlers for the VFS interface.

Hash and bkey operations:
- `bch2_xattr_hash()` hashes xattr type plus name.
- `xattr_hash_key()`, `xattr_hash_bkey()`, `xattr_cmp_key()`, and `xattr_cmp_bkey()` adapt xattrs to `bch_hash_desc`.
- `bch2_xattr_hash_desc` targets `BTREE_ID_xattrs` and `KEY_TYPE_xattr`.
- `bch2_xattr_validate()` checks value size bounds, xattr type validity, and NUL characters in names.
- `bch2_xattr_to_text()` prints namespace prefix, name/value text, and ACL details for POSIX ACL xattrs.

Core xattr operations:
- `bch2_xattr_get_trans()` looks up an xattr by type/name and copies its value to the caller.
- `bch2_xattr_set()` checks subvolume read-only state, peeks/writes inode ctime to ensure snapshot inode presence, then inserts/replaces/deletes the xattr hash entry.
- Delete of a missing key maps to success unless `XATTR_REPLACE` was requested.

Listing:
- `bch2_xattr_emit()` emits normal xattr names through namespace handlers.
- `bch2_xattr_list_bcachefs()` lists synthetic `bcachefs.*` and `bcachefs_effective.*` inode option xattrs.
- `bch2_xattr_list()` scans the xattr btree in the inode subvolume and appends synthetic inode-option attributes.

VFS handlers:
- Provides user, trusted, and security handlers.
- Trusted listing requires `CAP_SYS_ADMIN`.
- POSIX ACL types map to nop ACL handlers for type recognition.

Bcachefs synthetic xattrs:
- `bcachefs.*` gets/sets explicitly defined inode options.
- `bcachefs_effective.*` exposes inherited/effective option values and ignores sets.
- Setting options parses option text, runs option hooks, handles casefold changes, validates 31-bit directory offset mode on empty dirs, updates project id accounting, and writes the inode.

Important behavior:
- Xattr updates always touch the inode ctime and write the inode before xattr btree mutation so snapshot metadata remains coherent.
- Xattr key size is bounded by `u8 k.u64s`; oversized values return `-ERANGE`.
