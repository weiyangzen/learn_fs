# sources/distributed-fs/ceph-client/fs/squashfs/lzo_wrapper.c

## Purpose

This wrapper implements SquashFS LZO decompression using the kernel LZO library.

## Important APIs, Types, and Functions

It exports `squashfs_lzo_comp_ops`. Internal state is `struct squashfs_lzo` with input and output buffers. Functions are `lzo_init()`, `lzo_free()`, and `lzo_uncompress()`.

## Control Flow

Init allocates vmalloc input/output buffers sized to the larger of block size and metadata size. Decompress copies BIO input into the input buffer, calls `lzo1x_decompress_safe()`, and copies the produced bytes to the output actor.

## State and Persistence Behavior

Workspace buffers persist per backend stream. Output persists only through cache/page-cache consumers.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_LZO`, uses `<linux/lzo.h>`, and is registered through `decompressor.c`.

## Risks and Edge Cases

Allocation failure must free partially allocated buffers. Any non-`LZO_E_OK` result becomes `-EIO`. Since it stages both input and output, large block sizes increase memory use per decompressor stream.

## Test Signals

Mount/read LZO images, corruption tests for compressed data, allocation-failure injection, and parallel read tests with multi decompressor streams.
