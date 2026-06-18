<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/Makefile -->
# sources/distributed-fs/ceph-client/fs/Makefile

## Purpose
This top-level filesystem Makefile maps core VFS objects and configured filesystem subdirectories into the kernel build.

## Important APIs, types, and functions
It uses kbuild `obj-y` and `obj-$(CONFIG_*)` lists. Relevant mappings include core VFS objects, `obj-$(CONFIG_NETFS_SUPPORT) += netfs/`, `obj-$(CONFIG_ADFS_FS) += adfs/`, and `obj-$(CONFIG_9P_FS) += 9p/`.

## Control flow
Kbuild compiles always-on VFS core files first, then conditionally descends into helper and filesystem subdirectories based on `.config`. Ordering comments preserve behavior such as ext4 before ext2.

## State and persistence
No runtime state. It persists build graph decisions for the configured kernel.

## Dependencies and integration points
It connects top-level Kconfig symbols to actual code directories and shared VFS infrastructure.

## Risks and test signals
Risks include wrong ordering, stale config names, omitted helper directories, and module/built-in link problems. Test signals include broad config builds and verifying selected filesystems produce objects/modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/Makefile -->
