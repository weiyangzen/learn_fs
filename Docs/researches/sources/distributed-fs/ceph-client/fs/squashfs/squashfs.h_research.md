# sources/distributed-fs/ceph-client/fs/squashfs/squashfs.h

## Purpose

This is the internal SquashFS header that ties the implementation together. It declares logging macros, shared helper APIs, decompressor thread operations, and VFS operation tables exported across compilation units.

## Important APIs, Types, and Functions

Important macros are `TRACE`, `ERROR`, `WARNING`, and `SQUASHFS_READ_PAGES`. The key type is `struct squashfs_decompressor_thread_ops`. The header declares all cross-file helpers for block reads, caches, metadata, decompressor setup, export tables, fragment/id/xattr table lookup, inode loading, file reads, directory/file/symlink/inode ops, and xattr handlers.

## Control Flow

No code flow beyond declarations. It defines the shared call graph: `super.c` initializes state; `inode.c`, `dir.c`, `namei.c`, `file.c`, `xattr.c`, and export code use cache/block/decompressor helpers through this contract.

## State and Persistence Behavior

It declares interfaces that manipulate per-mount `squashfs_sb_info`, per-inode `squashfs_inode_info`, and temporary cache/page actor state, but owns no storage.

## Dependencies and Integration Points

Included by most SquashFS `.c` files. The conditional externs for thread ops mirror Kconfig selections and Makefile object inclusion.

## Risks and Edge Cases

Prototype drift causes build failures or worse if signatures diverge from implementations. `SQUASHFS_READ_PAGES` changes the `read_page` cache size depending on file-cache mode.

## Test Signals

All SquashFS build configurations and sparse checking are the primary validation signals for this internal interface.
