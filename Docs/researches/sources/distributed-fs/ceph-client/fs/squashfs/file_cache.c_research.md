# sources/distributed-fs/ceph-client/fs/squashfs/file_cache.c

## Purpose

`file_cache.c` implements the file-data strategy that decompresses each compressed data block into an intermediate SquashFS cache entry and then copies it into page-cache folios.

## Important APIs, Types, and Functions

It defines `squashfs_readpage_block()`, the strategy function declared in `squashfs.h` and called by `file.c`.

## Control Flow

For a requested folio, the function gets the compressed data block through `squashfs_get_datablock()`, checks `buffer->error`, copies the expected bytes into the relevant page-cache folios using `squashfs_copy_cache()`, then releases the cache entry.

## State and Persistence Behavior

It uses the per-mount `read_page` cache as temporary decompressed storage. Successful copies persist in the VFS page cache.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_FILE_CACHE`. It depends on `cache.c` and `file.c` and is mutually exclusive with `file_direct.c`.

## Risks and Edge Cases

The extra copy costs CPU and memory bandwidth but reduces direct page-cache locking complexity. Error propagation depends on `buffer->error`, and the cache must be available when this strategy is compiled.

## Test Signals

Read tests with `SQUASHFS_FILE_CACHE`, fragment vs normal data paths, repeated reads to see cache reuse, and comparison against direct mode.
