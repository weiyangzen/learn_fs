# sources/distributed-fs/ceph-client/fs/minix/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/Makefile` defines how the Minix filesystem driver is built. The source was read as a complete 8-line file for this report.

## Important APIs, Types, and Functions

The build variables are `obj-$(CONFIG_MINIX_FS) += minix.o` and `minix-objs := bitmap.o itree_v1.o itree_v2.o namei.o inode.o file.o dir.o`.

## Control Flow

There is no runtime flow. Kbuild links the listed object files into `minix.o` when `CONFIG_MINIX_FS` is enabled.

## State and Persistence Behavior

No runtime state is owned. The file controls build composition only.

## Dependencies and Integration Points

It integrates with Kbuild and the `MINIX_FS` Kconfig symbol. The object list ties allocation bitmap handling, inode tree implementations, name lookup, inode operations, regular file operations, and directory operations into one filesystem module.

## Risks and Edge Cases

Missing any listed object would create unresolved symbols or incomplete filesystem behavior. Adding source files without updating this list would leave them unbuilt.

## Test Signals

Build Minix as built-in and module, verify all object files link, and run a mount/read/write smoke test on Minix images after build changes.
