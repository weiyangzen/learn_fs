# sources/distributed-fs/ceph-client/fs/jffs2/xattr_trusted.c

## Purpose
Registers the JFFS2 `trusted.*` xattr namespace handler.

## Important APIs, types, and functions
`jffs2_trusted_getxattr()` and `jffs2_trusted_setxattr()` delegate to common helpers with `JFFS2_XPREFIX_TRUSTED`. `jffs2_trusted_listxattr()` allows listing only with `CAP_SYS_ADMIN`. `jffs2_trusted_xattr_handler` exposes prefix, list, get, and set callbacks.

## Control flow
The VFS xattr layer dispatches trusted namespace operations here; storage and persistence are handled entirely by `xattr.c`.

## State and persistence behavior
No local state. Trusted values persist as normal JFFS2 xattr datum/xref nodes with a trusted prefix.

## Dependencies and integration points
Depends on Linux xattr handler contracts, capability checks, JFFS2 prefix constants, and shared xattr helpers.

## Risks and test signals
Test privileged get/set/list, unprivileged list hiding, remount persistence, and namespace prefix correctness.
