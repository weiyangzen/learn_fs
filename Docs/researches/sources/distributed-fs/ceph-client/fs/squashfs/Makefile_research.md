# sources/distributed-fs/ceph-client/fs/squashfs/Makefile

## Purpose

This Makefile wires the SquashFS source files into the kernel build. It always builds the core object set for `CONFIG_SQUASHFS` and conditionally appends file-data, decompressor-thread, xattr, and compression-wrapper objects according to Kconfig.

## Important APIs, Types, and Functions

The important build targets are `obj-$(CONFIG_SQUASHFS) += squashfs.o` and `squashfs-y` component lists. Core objects are `block.o`, `cache.o`, `dir.o`, `export.o`, `file.o`, `fragment.o`, `id.o`, `inode.o`, `namei.o`, `super.o`, `symlink.o`, `decompressor.o`, and `page_actor.o`.

## Control Flow

Build flow follows Kbuild aggregation: `squashfs.o` is linked from the unconditional object list plus conditionally selected objects. Exactly one file read implementation is expected from the file decompression choice; one or more thread implementations may be linked when mount-time choice is enabled.

## State and Persistence Behavior

No runtime state is owned here. The Makefile defines which symbols and object implementations are present in the final module or built-in kernel image.

## Dependencies and Integration Points

It depends on the Kconfig symbols in this directory. It integrates with kernel Kbuild and the exported symbols expected by `super.c`, `decompressor.c`, and `squashfs.h`.

## Risks and Edge Cases

Missing an object for a selected Kconfig symbol produces unresolved symbols, especially for compression wrappers or thread ops referenced by `super.c` and `decompressor.c`. Accidentally linking multiple file data strategies with the same `squashfs_readpage_block` symbol would conflict, so the Kconfig choice must remain exclusive.

## Test Signals

Build matrix coverage across compression backends, xattr on/off, file cache/direct choices, and each decompressor mode is the primary signal.
