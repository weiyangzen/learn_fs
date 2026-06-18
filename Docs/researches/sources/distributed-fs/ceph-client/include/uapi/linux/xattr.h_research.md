<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xattr.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/xattr.h

Purpose: defines extended attribute operation flags, optional `xattr_args`, namespace prefixes, and standard security/system attribute names.

Important APIs and types: under libc compatibility, `XATTR_CREATE`, `XATTR_REPLACE`, and `struct xattr_args` support xattr set semantics and aligned user pointers. Namespace prefixes include OS/2, macOS, btrfs, GNU/Hurd, security, system, trusted, and user. Named security attributes include EVM, IMA, SELinux, SMACK variants, AppArmor, capabilities, and BPF LSM. POSIX ACL xattr names are defined under `system.`.

Control flow, state, and persistence: xattr syscalls use names and flags to create, replace, list, get, or remove filesystem metadata. Attribute values persist on filesystem objects subject to filesystem support.

Dependencies and integration points: integrates VFS xattr handlers, LSMs, IMA/EVM, capabilities, POSIX ACLs, and libc header compatibility.

Risks and test signals: risks include libc duplicate definitions, namespace permission mistakes, name length assumptions, and security attribute interoperability. Test setxattr flags, all namespaces, ACL/capability xattrs, LSM labels, and filesystem round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xattr.h -->
