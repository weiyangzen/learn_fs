<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/Makefile -->
# sources/distributed-fs/ceph-client/fs/efs/Makefile

## Purpose
The Makefile defines how the EFS filesystem object is assembled.

## Important APIs, types, and functions
`obj-$(CONFIG_EFS_FS)` builds `efs.o`, composed from `super.o`, `inode.o`, `namei.o`, `dir.o`, `file.o`, and `symlink.o`.

## Control flow
No runtime control flow exists. Kbuild uses the object list when `CONFIG_EFS_FS` is enabled.

## State and persistence
No state is stored. It controls compile-time composition.

## Dependencies and integration points
It integrates EFS VFS, inode, lookup, directory, regular-file, and symlink pieces into one module.

## Risks and test signals
Risks are stale object lists after source movement and missing build coverage for module/built-in forms. Test signals are EFS builds in all supported configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/Makefile -->
