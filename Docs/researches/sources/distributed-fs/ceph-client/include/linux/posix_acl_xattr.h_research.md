# sources/distributed-fs/ceph-client/include/linux/posix_acl_xattr.h

Purpose: declares conversion helpers between in-kernel POSIX ACLs and extended-attribute wire format.

Important APIs and types: `posix_acl_xattr_size()` calculates serialized size for a count, `posix_acl_xattr_count()` validates and decodes entry count from a byte size, `posix_acl_from_xattr()` parses xattr data, `posix_acl_to_xattr()` serializes ACLs, `posix_acl_xattr_name()` maps ACL type to xattr name, `posix_acl_type()` maps xattr name to ACL type, and legacy no-op xattr handlers are declared.

Control flow: VFS/filesystem xattr paths receive an ACL xattr buffer, validate its size/count, parse it into a `struct posix_acl`, validate/use it, and serialize kernel ACLs back to user-visible xattr format for reads.

State and persistence: no state is stored here. The xattr byte representation is the persistent filesystem/user ABI; kernel ACL objects are temporary or cached elsewhere.

Dependencies and integration points: integrates UAPI xattr and POSIX ACL xattr layouts with `linux/posix_acl.h`, user namespace ID translation, and filesystem xattr handlers. Parsing returns `-EOPNOTSUPP` when POSIX ACL support is disabled.

Risks and test signals: risks include accepting malformed sizes, wrong ACL type/name mapping, UID/GID namespace conversion mistakes, buffer sizing errors, and use of legacy no-op handlers in new code. Test xattr round trips, malformed xattr lengths, access/default name mapping, idmapped mount ACL serialization, and disabled ACL builds.
