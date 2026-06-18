# sources/distributed-fs/ceph-client/fs/affs/Makefile

## Purpose
The AFFS Makefile maps `CONFIG_AFFS_FS` to the composite `affs.o` filesystem module or built-in object.

## Important APIs, types, and functions
It defines `obj-$(CONFIG_AFFS_FS) += affs.o` and composes `affs-objs` from `super.o`, `namei.o`, `inode.o`, `file.o`, `dir.o`, `amigaffs.o`, `bitmap.o`, and `symlink.o`.

## Control flow
kbuild evaluates `CONFIG_AFFS_FS` and links the listed object files into one AFFS driver object. The commented `ccflags-y` debug line indicates optional local debug builds.

## State and persistence
This file has build-graph state only.

## Dependencies and integration points
It must stay synchronized with `Kconfig`, exported symbols in `affs.h`, and module metadata in `super.c`.

## Risks and test signals
Risks include missing a new source file from `affs-objs`, stale object names after file renames, or debug flags leaking into builds. Test signals are module and built-in builds plus link checks for all AFFS object exports.
