# sources/distributed-fs/ceph-client/fs/squashfs/decompressor.c

## Purpose

`decompressor.c` is the SquashFS decompressor registry and setup layer. It maps on-disk compression IDs to compiled backend operations, reports unsupported algorithms, reads optional compression options from the image, and creates the selected threaded decompressor stream.

## Important APIs, Types, and Functions

Public functions are `squashfs_lookup_decompressor()` and `squashfs_decompressor_setup()`. Internal `get_comp_opts()` reads optional compressor-specific metadata. The static `decompressor[]` table contains supported or unsupported `struct squashfs_decompressor` instances for zlib, lz4, lzo, xz, lzma, zstd, and unknown compression.

## Control Flow

Mount code uses `squashfs_lookup_decompressor()` after reading the superblock compression id. Later `squashfs_decompressor_setup()` calls `get_comp_opts()`; if the image has compression options, they are read as a metadata block immediately after the superblock and passed to the backend `comp_opts` hook. Finally the configured thread ops create the runtime stream.

## State and Persistence Behavior

This file owns no long-lived mutable state. It allocates transient option buffers and returns a stream owned by `msblk->stream` through the selected thread implementation. Unsupported compiled-out algorithms remain represented by read-only table entries with `supported = 0`.

## Dependencies and Integration Points

It integrates with `super.c`, `decompressor.h`, `squashfs_read_data()`, backend wrappers, and the thread ops selected by Kconfig/mount options.

## Risks and Edge Cases

Images using unsupported compression must fail cleanly. Bad or truncated compression option blocks must fail mount, not leak buffers. The setup path assumes `msblk->decompressor` and `msblk->thread_ops` are already initialized by `super.c`.

## Test Signals

Mount images for each compiled backend; mount unsupported lzma or disabled-backend images; test images with and without compression options; inject corrupt option sizes for LZ4/XZ.
