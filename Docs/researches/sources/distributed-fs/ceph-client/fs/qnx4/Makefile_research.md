# sources/distributed-fs/ceph-client/fs/qnx4/Makefile

## Purpose
The Makefile builds the QNX4 filesystem object from its component source files.

## Important APIs, types, and functions
It maps `CONFIG_QNX4FS_FS` to `qnx4.o`, composed from `inode.o`, `dir.o`, `namei.o`, and `bitmap.o`.

## Control flow
Kbuild links all QNX4 implementation units only when the filesystem is selected.

## State and persistence
No runtime state exists; it defines module composition.

## Dependencies and integration points
It integrates Kconfig selection with VFS filesystem registration code.

## Risks and test signals
Risks are missing object inclusion or stale build naming. Test signals are module and builtin builds plus `modinfo`/filesystem alias availability.
