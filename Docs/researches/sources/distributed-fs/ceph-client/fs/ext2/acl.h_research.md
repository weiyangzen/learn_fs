# sources/distributed-fs/ceph-client/fs/ext2/acl.h

Purpose: Defines ext2 on-disk ACL structures, sizing/counting helpers, and compile-time ACL stubs/prototypes.

Important APIs/types/functions: Defines `EXT2_ACL_VERSION`, `ext2_acl_entry`, `ext2_acl_entry_short`, `ext2_acl_header`, `ext2_acl_size`, and `ext2_acl_count`. When `CONFIG_EXT2_FS_POSIX_ACL` is enabled, it declares `ext2_get_acl`, `ext2_set_acl`, and `ext2_init_acl`; otherwise it maps get/set hooks to `NULL` and makes `ext2_init_acl` a no-op.

Control flow: `ext2_acl_size` encodes the ext2 disk format rule that the first four ACL entries are short entries and later named user/group entries require full entries. `ext2_acl_count` reverses that calculation and returns `-1` for misaligned/invalid payload sizes.

State and persistence behavior: No direct state mutation. It defines the persistent ACL wire format consumed by `acl.c`.

Dependencies and integration points: Includes `linux/posix_acl_xattr.h` and is included by ext2 inode/name/file creation paths. Its stubs keep callers buildable when POSIX ACL support is disabled.

Risks: Size/count helpers must stay exactly synchronized with the serializer; off-by-one or alignment mistakes can reject valid ACLs or overrun corrupt xattrs. The lack of include guards relies on existing include patterns and could be fragile if reused differently.

Test signals: Unit-style validation of ACL payload sizes around 0-5 entries; compile with ACL enabled and disabled; xattr parser tests for malformed ACL size.
