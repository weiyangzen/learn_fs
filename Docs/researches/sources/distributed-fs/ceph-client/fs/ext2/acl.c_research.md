# sources/distributed-fs/ceph-client/fs/ext2/acl.c

Purpose: Implements ext2 POSIX ACL support by translating between on-disk ext2 ACL xattr payloads and in-memory `struct posix_acl`.

Important APIs/types/functions: Public functions are `ext2_get_acl`, `ext2_set_acl`, and `ext2_init_acl`. Internal serializers are `ext2_acl_from_disk`, `ext2_acl_to_disk`, and `__ext2_set_acl`. The file uses xattr indexes `EXT2_XATTR_INDEX_POSIX_ACL_ACCESS` and `EXT2_XATTR_INDEX_POSIX_ACL_DEFAULT`.

Control flow: `ext2_get_acl` rejects RCU lookup, maps ACL type to xattr index, probes xattr size, allocates a value buffer, rereads the xattr, and converts it to `posix_acl`. `ext2_set_acl` updates mode bits for access ACLs via `posix_acl_update_mode`, stores or removes the xattr with `__ext2_set_acl`, then updates mode/ctime if needed. `ext2_init_acl` derives ACLs from the parent with `posix_acl_create` and writes default/access ACLs for a new inode.

State and persistence behavior: ACLs persist as extended attribute blocks/entries. Successful writes update the inode ACL cache with `set_cached_acl`; access ACL updates may change `inode->i_mode`, ctime, and dirty state. Default ACLs are rejected for non-directories unless clearing them.

Dependencies and integration points: Depends on ext2 xattr helpers, Linux POSIX ACL core, id conversion through `init_user_ns`, and VFS inode operation hooks from `file.c` and `namei.c`.

Risks: Disk format parsing is sensitive to short-vs-full entry sizing, version checks, exact end-pointer consumption, and invalid tags. `init_user_ns` mapping means ACL IDs are serialized in the initial namespace. Allocation failures must not partially update ACL cache or mode.

Test signals: ACL get/set/remove on files and directories; inherited default ACL creation; chmod interactions; corrupt xattr ACL payloads with bad version, length, tag, or trailing bytes; builds with ACL disabled using stubs from `acl.h`.
