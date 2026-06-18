# sources/distributed-fs/ceph-client/fs/squashfs/decompressor_single.c

## Purpose

This file implements the legacy single-stream decompressor mode. It serializes all SquashFS decompression for a mount behind one mutex-protected backend stream.

## Important APIs, Types, and Functions

It exports `squashfs_decompressor_single`. Internal `struct squashfs_stream` holds `void *stream` and a mutex. Functions are `squashfs_decompressor_create()`, `squashfs_decompressor_destroy()`, `squashfs_decompress()`, and `squashfs_max_decompressors()`.

## Control Flow

Create allocates one wrapper and backend stream, frees compression options, and initializes the mutex. Decompression locks the mutex, calls the backend, unlocks, and reports corrupt data on negative return. Destroy frees the backend stream and wrapper.

## State and Persistence Behavior

Per-mount state is a single stream in `msblk->stream`. It minimizes memory use but creates a bottleneck for concurrent reads.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_DECOMP_SINGLE` and used as the default in `super.c` when compiled. `block.c` calls through this implementation via thread ops.

## Risks and Edge Cases

The primary risk is performance under parallel I/O, not correctness. Initialization must free wrapper memory on backend init failure.

## Test Signals

Basic mount/read coverage, lockdep with parallel readers, and performance comparison against multi/percpu modes.
