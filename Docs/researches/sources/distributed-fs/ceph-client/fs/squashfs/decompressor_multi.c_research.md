# sources/distributed-fs/ceph-client/fs/squashfs/decompressor_multi.c

## Purpose

This file implements the dynamic multi-decompressor thread mode. It maintains a pool of algorithm-specific decompressor streams and lets parallel I/O callers borrow streams up to `msblk->max_thread_num`.

## Important APIs, Types, and Functions

It exports `squashfs_decompressor_multi`, a `struct squashfs_decompressor_thread_ops`. Internal types are `struct squashfs_stream` for pool state and `struct decomp_stream` for individual backend streams. Internal helpers include `squashfs_max_decompressors()`, `squashfs_decompressor_create()`, `squashfs_decompressor_destroy()`, `get_decomp_stream()`, `put_decomp_stream()`, and `squashfs_decompress()`.

## Control Flow

Create allocates the pool and one default stream so the filesystem can operate even if later dynamic allocation fails. Decompression borrows an available stream, dynamically allocates another if below the max and memory allows, otherwise waits for a stream to return. After backend decompression, it returns the stream to the list and wakes waiters.

## State and Persistence Behavior

Per-mount pool state lives in `msblk->stream`. It owns `comp_opts`, a mutex-protected list of available streams, `avail_decomp`, and a wait queue. Individual backend streams persist until unmount.

## Dependencies and Integration Points

It is selected by `CONFIG_SQUASHFS_DECOMP_MULTI` and used by `super.c` mount option parsing. It calls the selected `msblk->decompressor` backend hooks and is invoked by `block.c`.

## Risks and Edge Cases

Pool accounting must remain balanced during allocation failure and unmount. Waiting uses stream availability, so a leaked stream would deadlock future reads. `max_thread_num` must not exceed the advertised maximum.

## Test Signals

Parallel read/readahead benchmarks, memory-pressure allocation-failure tests, numeric `threads=` mount tests, and unmount under active read stress are useful.
