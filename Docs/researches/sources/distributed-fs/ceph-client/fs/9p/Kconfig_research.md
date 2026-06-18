<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/Kconfig -->
# sources/distributed-fs/ceph-client/fs/9p/Kconfig

## Purpose
This Kconfig fragment exposes Linux 9P filesystem support and optional caching, POSIX ACL, and security-label features.

## Important APIs, types, and functions
Symbols are `CONFIG_9P_FS`, `CONFIG_9P_FSCACHE`, `CONFIG_9P_FS_POSIX_ACL`, and `CONFIG_9P_FS_SECURITY`.

## Control flow
`9P_FS` depends on `NET_9P` and selects `NETFS_SUPPORT`. Optional symbols gate FS-Cache integration, POSIX ACL handlers, and security xattr handlers.

## State and persistence
Only build configuration is persisted in `.config`. Runtime behavior is selected through compiled objects and mount options.

## Dependencies and integration points
It integrates 9p with the net/9p client, netfs library, FS-Cache, generic POSIX ACL helpers, and LSM security xattrs.

## Risks and test signals
Risks include invalid dependency combinations, especially built-in 9p with modular FS-Cache. Test signals include allmodconfig/randconfig, ACL option availability, and security xattr handler builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/Kconfig -->
