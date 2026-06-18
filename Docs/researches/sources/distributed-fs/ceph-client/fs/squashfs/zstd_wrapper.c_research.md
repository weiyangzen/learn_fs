# sources/distributed-fs/ceph-client/fs/squashfs/zstd_wrapper.c

## Purpose

This wrapper implements SquashFS Zstandard decompression using the kernel zstd streaming API.

## Important APIs, Types, and Functions

It exports `squashfs_zstd_comp_ops`. Internal `struct workspace` stores workspace memory, size, and window size. Functions are `zstd_init()`, `zstd_free()`, and `zstd_uncompress()`.

## Control Flow

Init computes a window size from max(block size, metadata size), asks zstd for workspace bound, and vmallocs memory. Decompress initializes a dstream on that workspace, feeds BIO segments into `zstd_decompress_stream()`, advances actor output pages as output buffers fill, stops when zstd returns 0, and returns total produced bytes.

## State and Persistence Behavior

Each backend stream owns one reusable workspace. Decompression stream state is initialized inside that workspace per call.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_ZSTD`, uses `<linux/zstd.h>`, and sets `alloc_buffer = 1` for direct actor fallback behavior.

## Risks and Edge Cases

Workspace sizing must match the maximum possible block/window. The total output accounting subtracts prior `out_buf.pos` before each stream call and adds the new position; regressions here would produce wrong byte counts and failed page reads. Running out of actor pages before stream completion is `-EIO`.

## Test Signals

Zstd image reads across block sizes, corrupt streams, direct mode with page gaps, parallel multi-stream reads, and memory-pressure initialization tests.
