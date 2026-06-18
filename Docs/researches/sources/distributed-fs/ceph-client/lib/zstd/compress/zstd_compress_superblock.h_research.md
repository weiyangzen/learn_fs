<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.h

## Purpose
`zstd_compress_superblock.h` declares the private advanced compression entry point for target compressed block sizing.

## Important APIs, Types, and Functions
It includes `<linux/zstd.h>` for `ZSTD_CCtx` and declares `ZSTD_compressSuperBlock(ZSTD_CCtx* zc, void* dst, size_t dstCapacity, void const* src, size_t srcSize, unsigned lastBlock)`.

## Control Flow
Callers invoke `ZSTD_compressSuperBlock()` after matchfinding has populated the context sequence store. The function compresses the provided source block into one or more Zstd blocks sized around the context target, setting the final block marker according to `lastBlock`.

## State and Persistence
The header has no state. The declared function uses and updates state inside `ZSTD_CCtx`, especially sequence storage, entropy tables, block state, temporary workspace, BMI2 flag, and applied compression parameters.

## Dependencies and Integration Points
This header is used by the main compressor when `targetCBlockSize` is active. It intentionally exposes only the single superblock function rather than the subblock helpers.

## Risks
The API relies on an initialized `ZSTD_CCtx` with a valid sequence store and temporary workspace. Calling it outside the normal block-compression flow would violate hidden invariants from `zstd_compress_internal.h`.

## Test Signals
Compile coverage should ensure the main compressor can include this header in kernel-style builds. Runtime tests should enable target compressed block size and verify last-block handling, size targeting, fallback behavior, and decompression round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_superblock.h -->
