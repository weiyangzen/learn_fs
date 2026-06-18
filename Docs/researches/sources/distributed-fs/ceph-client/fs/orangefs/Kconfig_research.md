## sources/distributed-fs/ceph-client/fs/orangefs/Kconfig

### Purpose
This Kconfig entry exposes OrangeFS, also known as PVFS, as an optional Linux filesystem.

### Important APIs, types, and functions
- `config ORANGEFS_FS` defines a tristate option named `ORANGEFS (Powered by PVFS) support`.
- `select FS_POSIX_ACL` enables POSIX ACL support for OrangeFS builds.

### Control flow
When selected as built-in or module, Kbuild includes the OrangeFS object list from the companion Makefile and compiles the VFS client.

### State and persistence behavior
No runtime state is present. The file expresses build-time feature selection.

### Dependencies and integration points
The selected ACL dependency matches OrangeFS inode operations that export `.get_inode_acl` and `.set_acl`, and the xattr-backed ACL implementation in `acl.c`.

### Risks
The help text is brief and does not mention the required userspace daemon and `/dev/pvfs2-req` interface, which can surprise operators enabling only the kernel config.

### Test signals
Kernel config tests should confirm that `CONFIG_ORANGEFS_FS=m` builds the `orangefs.ko` module and that `FS_POSIX_ACL` is enabled when OrangeFS is selected.
