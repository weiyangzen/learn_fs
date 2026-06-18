# sources/distributed-fs/ceph-client/fs/hfs/Makefile

## Purpose
The HFS Makefile defines how the kernel builds the HFS filesystem module or built-in object and its optional KUnit test object.

## Important Targets
`obj-$(CONFIG_HFS_FS) += hfs.o` builds the aggregate HFS object when configured. `hfs-objs` lists component objects: bitmap, B-tree find/node/record/tree, catalog, dir, extent, inode, attr, mdb, partition table, string, super, sysdep, and trans support. `obj-$(CONFIG_HFS_KUNIT_TEST) += string_test.o` adds the string KUnit test object when enabled.

## Control Flow And State
There is no runtime behavior. Build composition determines which `.c` files are linked into `hfs.o`, so dependencies among HFS internals are resolved at link time.

## Dependencies And Integration Points
The file consumes `CONFIG_HFS_FS` and `CONFIG_HFS_KUNIT_TEST` from Kconfig. It integrates all core HFS implementation files into one filesystem object.

## Risks And Test Signals
Risks include omitting a new source file from `hfs-objs`, stale test target names, or adding order-sensitive objects incorrectly. Signals are successful built-in and module builds, modpost output, and KUnit test linkage.
