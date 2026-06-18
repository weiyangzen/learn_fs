# sources/distributed-fs/ceph-client/fs/qnx6/Makefile

## Purpose
The Makefile builds the QNX6 filesystem object and applies optional debug flags.

## Important APIs, types, and functions
It maps `CONFIG_QNX6FS_FS` to `qnx6.o`, composed from `inode.o`, `dir.o`, `namei.o`, and `super_mmi.o`, and adds `-DDEBUG` for `CONFIG_QNX6FS_DEBUG`.

## Control flow
Kbuild links all QNX6 source units only when the filesystem is selected.

## State and persistence
No runtime state exists here.

## Dependencies and integration points
It integrates QNX6 Kconfig symbols with VFS module build output.

## Risks and test signals
Risks include stale comment naming QNX4 and missing source objects. Test signals are normal, debug, module, and builtin builds.
