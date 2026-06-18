## sources/distributed-fs/beegfs/meta/source/storage/PosixACL.cpp

Purpose: Implements POSIX ACL xattr serialization/deserialization and mode-bit reconciliation for metadata-created entries.

Important APIs/types/functions: `defaultACLXAttrName` and `accessACLXAttrName` name Linux POSIX ACL xattrs. `deserializeXAttr()` validates `POSIX_ACL_XATTR_VERSION` then deserializes `ACLEntry` objects. `serializeXAttr()` computes serialized size then fills the buffer. `modifyModeBits()` transforms ACL permissions using a requested file mode and reports whether an ACL xattr remains needed. `toString()` provides debug rendering.

Control flow: Deserialization reads a version first and then loops until the deserializer consumes the input. Serialization intentionally runs twice to size then write. `modifyModeBits()` scans all ACL entries, handling owner, named users/groups, group object, mask, and other entries; after the scan it resolves group bits through the mask if present, otherwise through the group object.

State and persistence: The class owns an in-memory vector of ACL entries. Serialized output is persisted as `system.posix_acl_default` or `system.posix_acl_access` xattrs elsewhere. `modifyModeBits()` mutates entries and updates the passed mode bits.

Dependencies and integration: Depends on BeeGFS `Serializer`/`Deserializer`, `FhgfsOpsErr`, `CharVector`, and the entry layout declared in `PosixACL.h`. It integrates with metadata create/inherit-ACL paths and xattr storage.

Risks and test signals: `deserializeXAttr()` takes `&xattr[0]`; empty input would be unsafe unless callers reject it. ACLs missing a group/mask entry return `FhgfsOpsErr_INTERNAL`. Tests should cover empty/malformed xattrs, version mismatch, named-user/group ACLs needing persistence, mask-vs-group interactions, and round-trip serialization.
