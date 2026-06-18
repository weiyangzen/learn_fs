# sources/distributed-fs/ceph-client/fs/squashfs/zlib_wrapper.c

## Purpose

This wrapper implements the default SquashFS ZLIB decompression backend using the kernel zlib inflate implementation.

## Important APIs, Types, and Functions

It exports `squashfs_zlib_comp_ops`. Functions are `zlib_init()`, `zlib_free()`, and `zlib_uncompress()`. Runtime state is a `z_stream` plus vmalloced inflate workspace.

## Control Flow

Init allocates a zlib stream and workspace. Decompress lazily calls `zlib_inflateInit()`, feeds BIO segment input when `avail_in` is empty, advances actor output pages when `avail_out` reaches zero, runs `zlib_inflate(Z_SYNC_FLUSH)` until `Z_STREAM_END`, then calls `zlib_inflateEnd()` and returns `stream->total_out`.

## State and Persistence Behavior

The workspace persists per backend stream. `z_stream` fields are reused per decompression call and finalized after each call.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_ZLIB`, uses `<linux/zlib.h>`, and sets `alloc_buffer = 1` for direct actor fallback behavior.

## Risks and Edge Cases

Failure before `zlib_inflateInit()` must not call inflateEnd incorrectly. Streaming must not run out of actor pages before stream end. zlib errors map to `-EIO`.

## Test Signals

Default zlib image reads, corrupt/truncated streams, direct and cached file modes, metadata-heavy directory traversal, and all decompressor thread modes.
