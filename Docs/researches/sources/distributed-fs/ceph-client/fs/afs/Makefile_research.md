# sources/distributed-fs/ceph-client/fs/afs/Makefile

## Purpose
The AFS Makefile links the kAFS client from many subsystem objects and conditionally includes procfs support.

## Important APIs, types, and functions
It defines `kafs-y` with address, callback, cell, directory, file, fsclient, RxRPC, security, server, superblock, VL, volume, write, xattr, and YFS client objects. `kafs-$(CONFIG_PROC_FS)` adds `proc.o`, and `obj-$(CONFIG_AFS_FS) := kafs.o` links the composite object.

## Control flow
kbuild includes the complete AFS client object list when `AFS_FS` is enabled and omits procfs integration when `CONFIG_PROC_FS` is disabled.

## State and persistence
This is build-graph state only.

## Dependencies and integration points
It must remain synchronized with Kconfig dependencies and cross-file symbols in `internal.h`.

## Risks and test signals
Risks include missing newly introduced objects, link failures when procfs is disabled, or stale object names. Test signals include `AFS_FS=y/m`, `PROC_FS=n`, and full symbol link checks under security feature matrices.
