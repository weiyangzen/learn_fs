# sources/distributed-fs/ceph-client/fs/squashfs/decompressor.h

## Purpose

This header defines the backend decompressor interface used by SquashFS. It separates algorithm-specific init/options/free/decompress functions from the higher-level thread-mode wrappers.

## Important APIs, Types, and Functions

The central type is `struct squashfs_decompressor`, with hooks `init`, `comp_opts`, `free`, and `decompress`, fields `id`, `name`, `alloc_buffer`, and `supported`. The helper `squashfs_comp_opts()` invokes an optional backend option parser. Conditional externs declare compiled wrappers for XZ, LZ4, LZO, ZLIB, and ZSTD.

## Control Flow

There is no standalone control flow. `decompressor.c` and the thread wrappers call through this interface during mount setup and block decompression.

## State and Persistence Behavior

The struct describes immutable backend operations. Backend `init()` creates per-stream state; `alloc_buffer` influences `page_actor` behavior for direct decompression.

## Dependencies and Integration Points

The header includes `linux/bio.h` and references `struct squashfs_sb_info` and `struct squashfs_page_actor`. It is shared by `block.c`, `decompressor.c`, `decompressor_*`, `page_actor.c`, and all compression wrappers.

## Risks and Edge Cases

Changing hook signatures or `alloc_buffer` semantics affects every backend and direct page-cache decompression. A backend returning an incorrect byte count can corrupt page-cache state in callers.

## Test Signals

Compile coverage for every backend, sparse/smatch type checking, and mount/read tests across direct and cached file modes validate this interface.
