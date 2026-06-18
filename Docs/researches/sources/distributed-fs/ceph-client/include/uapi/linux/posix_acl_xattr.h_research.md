<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl_xattr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl_xattr.h

Purpose: defines the on-xattr wire format for POSIX ACLs exposed to userspace.

Important APIs and types: `POSIX_ACL_XATTR_VERSION` is the supported ACL xattr version. `struct posix_acl_xattr_header` stores little-endian `a_version`, and `struct posix_acl_xattr_entry` stores little-endian tag, permission, and ID fields.

Control flow: userspace reads or writes ACL xattrs; the kernel validates the header version and converts each serialized xattr entry to in-kernel ACL entries before applying permissions.

State and persistence: ACL xattr data persists in filesystem extended attributes. All multibyte fields are little-endian, making the xattr format independent of host CPU endianness.

Dependencies and integration points: depends on Linux integer/endian types and integrates with VFS ACL helpers, filesystem xattr storage, NFS/export tools, and ACL utilities.

Risks and test signals: risks include endian conversion errors, malformed variable-length xattrs, version mismatch, and incorrect `ACL_UNDEFINED_ID` handling. Test xattr round trips on big/little endian builds, invalid lengths, unknown versions, and ACL enforcement after restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/posix_acl_xattr.h -->
