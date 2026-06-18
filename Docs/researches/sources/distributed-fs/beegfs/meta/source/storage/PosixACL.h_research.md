## sources/distributed-fs/beegfs/meta/source/storage/PosixACL.h

Purpose: Declares the in-memory POSIX ACL representation used by metadata storage.

Important APIs/types/functions: `ACLEntry` mirrors Linux POSIX ACL xattr layout with `tag`, `perm`, and `id`, plus `POSIX_ACL_XATTR_VERSION` and tag constants. Its templated `serialize()` wires the struct into BeeGFS serialization. `PosixACL` exposes `deserializeXAttr()`, `serializeXAttr()`, `modifyModeBits()`, `toString()`, `empty()`, and xattr-name constants.

Control flow: No significant header-side flow beyond the serializer template and simple `empty()` check.

State and persistence: `PosixACL` stores private `ACLEntryVec entries`; serialized form maps to Linux ACL xattrs and affects persisted file mode bits.

Dependencies and integration: Pulls in BeeGFS serialization, common types, and storage errors. It is an adapter between Linux ACL xattr bytes and BeeGFS metadata create/update code.

Risks and test signals: The serialized struct layout must remain compatible with Linux `posix_acl_xattr_entry`. Tests should check endian/field-width assumptions through known byte vectors and compatibility with kernel-generated ACL xattrs.
