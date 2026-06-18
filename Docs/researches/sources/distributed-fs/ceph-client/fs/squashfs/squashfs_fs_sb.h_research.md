# sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs_sb.h

## Purpose

This header defines SquashFS per-superblock state and cache entry structures used for a mounted filesystem.

## Important APIs, Types, and Functions

`struct squashfs_cache` tracks cache geometry, current/next slots, unused count, waiters, spinlock, wait queue, and entries. `struct squashfs_cache_entry` tracks one cached decompressed block. `struct squashfs_sb_info` stores decompressor operations, device block sizing, caches, cache mapping, table indexes, metadata-index cache, decompressor stream, table starts, filesystem geometry/counts, error mode, thread ops, and max thread count.

## Control Flow

There is no code flow here. `super.c` initializes and frees `squashfs_sb_info`; other modules read it for all filesystem operations.

## State and Persistence Behavior

This is the central per-mount persistent state. It persists from successful mount until `squashfs_put_super()` and owns all in-memory table indexes, caches, decompressor streams, and mount options.

## Dependencies and Integration Points

Included across the SquashFS implementation. Its fields connect mount-time table parsing to runtime file, directory, xattr, fragment, id, export, and decompression behavior.

## Risks and Edge Cases

Ownership and cleanup must match allocation paths in `super.c`; partial mount failure must handle NULL and ERR_PTR caches. Concurrency-sensitive fields include caches and the meta-index mutex/array.

## Test Signals

Mount failure injection, unmount leak checks, concurrent read/lookup workloads, xattr/export images, and all decompressor modes validate this state container.
