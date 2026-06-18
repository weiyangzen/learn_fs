# sources/distributed-fs/ceph-client/fs/squashfs/lz4_wrapper.c

## Purpose

This wrapper implements SquashFS LZ4 decompression backend support using the kernel LZ4 library and the legacy SquashFS LZ4 option format.

## Important APIs, Types, and Functions

It exports `squashfs_lz4_comp_ops`. Internal types are `struct lz4_comp_opts` and `struct squashfs_lz4`. Functions are `lz4_comp_opts()`, `lz4_init()`, `lz4_free()`, and `lz4_uncompress()`.

## Control Flow

Option parsing requires a present options block and validates the legacy version. Init allocates input and output vmalloc buffers sized to the larger of filesystem block size and metadata size. Decompress copies BIO segments into the input buffer, calls `LZ4_decompress_safe()`, then copies output into the page actor.

## State and Persistence Behavior

Each backend stream owns input/output work buffers until the decompressor thread mode frees it. No filesystem data is persisted beyond page-cache/cache consumers.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_LZ4`, uses `<linux/lz4.h>`, and plugs into `decompressor.c` through `struct squashfs_decompressor`.

## Risks and Edge Cases

LZ4 images without options or with non-legacy version are rejected. The full compressed input and decompressed output must fit allocated buffers. Return values below zero map to `-EIO`.

## Test Signals

Mount/read LZ4 images, corrupt options version, truncated compressed blocks, direct and cached file modes, and large block-size images.
