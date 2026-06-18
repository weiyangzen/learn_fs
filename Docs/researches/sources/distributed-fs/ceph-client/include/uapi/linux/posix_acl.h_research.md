<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl.h

Purpose: defines common POSIX ACL constants for ACL type, entry tag, undefined IDs, and permission bits.

Important APIs and types: `ACL_TYPE_ACCESS` and `ACL_TYPE_DEFAULT` classify access/default ACLs. Entry tags include `ACL_USER_OBJ`, `ACL_USER`, `ACL_GROUP_OBJ`, `ACL_GROUP`, `ACL_MASK`, and `ACL_OTHER`. Permission bits are `ACL_READ`, `ACL_WRITE`, and `ACL_EXECUTE`; `ACL_UNDEFINED_ID` marks entries without a user/group ID.

Control flow: filesystem and userspace ACL tools use these constants when translating ACL entries to permissions or xattrs. There is no executable flow in the header.

State and persistence: ACL state persists as filesystem metadata, commonly in extended attributes. The header only defines constants used to encode/decode that state.

Dependencies and integration points: integrates with VFS POSIX ACL handling, filesystem xattr implementations, backup/restore tools, and `getfacl`/`setfacl` style utilities.

Risks and test signals: risks include inconsistent interpretation of `ACL_MASK`, undefined IDs, and default ACL inheritance. Test ACL create/read/update/delete across filesystems, chmod interactions, xattr round trips, and permission checks for named user/group entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl.h -->
