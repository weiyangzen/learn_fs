# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/acl.h

Defines bcachefs on-disk ACL structures and declares ACL helper APIs.

Key elements:
- `BCH_ACL_VERSION` is the on-disk ACL format version.
- `bch_acl_header`, `bch_acl_entry_short`, and `bch_acl_entry` define the serialized ACL xattr format.
- Declares `bch2_acl_to_text()`.
- When filesystem/VFS support is enabled, declares `bch2_get_acl()`, `bch2_set_acl_trans()`, `bch2_set_acl()`, and `bch2_acl_chmod()`.
- Under `NO_BCACHEFS_FS`, transaction ACL set/chmod helpers are inline no-ops.

Filesystem relevance:
- This is the ACL format/API contract shared by xattr formatting, VFS hooks, and inode mode update code.
