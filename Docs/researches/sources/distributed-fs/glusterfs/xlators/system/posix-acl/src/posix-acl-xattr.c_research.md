# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-xattr.c

Purpose: binary xattr codec for Gluster's in-memory POSIX ACL representation. It parses Linux-style ACL xattr blobs into `struct posix_acl` and serializes ACLs back to xattr buffers.

Important APIs, types, and functions: `posix_ace_cmp()` orders ACEs by tag then ID. `posix_acl_normalize()` sorts ACL entries. `posix_acl_from_xattr()` validates header size, entry alignment, little-endian version, tag set, and IDs, then builds an ACL with `posix_acl_new()`. `posix_acl_to_xattr()` writes `posix_acl_xattr_header` and `posix_acl_xattr_entry` data, returning required size when the caller's buffer is too small. `posix_acl_matches_xattr()` decodes another ACL and compares entries.

Control flow: lookup/readdirp/setxattr paths in `posix-acl.c` call `from_xattr` when child translators return ACL blobs; inheritance paths call `to_xattr` to attach ACL xattrs to create requests; update paths use `matches_xattr` to avoid replacing cached ACLs when the xattr has not changed.

State and persistence: no global state. Persistent representation is the little-endian xattr blob stored by the lower POSIX xlator. In-memory ACL objects are ref-counted by `posix-acl.c`.

Dependencies and integration points: depends on endian conversion APIs, Gluster xlator types, `posix-acl.h`, and `glusterfs-acl.h` constants such as `POSIX_ACL_XATTR_VERSION`, ACL tags, and undefined ID.

Risks and test signals: `posix_acl_normalize()` calls `qsort()` with `sizeof(struct posix_ace *)` instead of `sizeof(struct posix_ace)`, which is suspicious because the array stores structs, not pointers. Invalid tags or malformed sizes fail parsing. Test signals should cover round-trip serialization, invalid version/size/tag rejection, deterministic ordering, and matching behavior.
