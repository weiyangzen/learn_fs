# sources/distributed-fs/ceph-client/fs/squashfs/xz_wrapper.c

## Purpose

This wrapper implements SquashFS XZ decompression using the kernel XZ decoder and optional on-disk dictionary-size options.

## Important APIs, Types, and Functions

It exports `squashfs_xz_comp_ops`. Internal types are `struct squashfs_xz`, `struct disk_comp_opts`, and `struct comp_opts`. Functions are `squashfs_xz_comp_opts()`, `squashfs_xz_init()`, `squashfs_xz_free()`, and `squashfs_xz_uncompress()`.

## Control Flow

Option parsing validates option length and dictionary size shape, or defaults to max(block size, metadata size). Init preallocates an XZ decoder with the dictionary size. Decompress resets the decoder, feeds BIO segments into `xz_dec_run()`, advances actor output pages as they fill, requires `XZ_STREAM_END`, and returns total output bytes.

## State and Persistence Behavior

Each stream owns an `xz_dec` state object and buffer descriptor. The parsed dictionary option is owned during stream creation.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_XZ`, uses `<linux/xz.h>`, and sets `alloc_buffer = 1`, which tells direct actors to provide temporary output for missing pages.

## Risks and Edge Cases

Dictionary validation is important for memory use and decoder correctness. Streaming output must handle actor error pointers and NULL pages. Missing `XZ_STREAM_END` is treated as corrupt input.

## Test Signals

XZ images with default and explicit dictionary options, corrupt option lengths/dictionary sizes, truncated streams, direct mode with missing pages, and memory-pressure tests.
