<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/Kconfig

## Purpose
This top-level filesystem Kconfig file organizes the kernel filesystem configuration menu, core filesystem helpers, pseudo filesystems, miscellaneous filesystems, and network filesystems.

## Important APIs, types, and functions
It defines symbols such as `DCACHE_WORD_ACCESS`, `VALIDATE_FS_PARSER`, `FS_IOMAP`, `FS_STACK`, `BUFFER_HEAD`, `LEGACY_DIRECT_IO`, `FS_DAX`, `FS_POSIX_ACL`, `EXPORTFS`, `FILE_LOCKING`, `MISC_FILESYSTEMS`, and `NETWORK_FILESYSTEMS`, and sources many subsystem Kconfig files including `fs/adfs/Kconfig` and `fs/9p/Kconfig`.

## Control flow
Kconfig conditionals gate submenus by `BLOCK`, `NET`, architecture capabilities, and parent menu choices. Selected symbols drive object inclusion in `fs/Makefile` and preprocessor conditionals throughout the kernel.

## State and persistence
The state is build-time `.config`. There is no runtime code.

## Dependencies and integration points
It integrates filesystem implementations with core kernel services such as netfs, cachefiles, crypto, verity, quota, notify, DAX, ACLs, and network stacks.

## Risks and test signals
Risks include broken dependency chains, unreachable filesystem options, invalid built-in/module combinations, and hidden helper symbols. Test signals include allnoconfig, allyesconfig, allmodconfig, randconfig, blockless configs, and network-disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/Kconfig -->
