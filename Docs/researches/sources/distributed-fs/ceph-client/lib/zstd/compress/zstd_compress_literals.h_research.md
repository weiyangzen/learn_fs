<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.h

## Purpose
`zstd_compress_literals.h` declares the private literals-section encoder API used by block and superblock compression code.

## Important APIs, Types, and Functions
It exposes `ZSTD_noCompressLiterals()`, `ZSTD_compressRleLiteralsBlock()`, and `ZSTD_compressLiterals()`. The declarations depend on `ZSTD_hufCTables_t`, `ZSTD_strategy`, `HUF_WORKSPACE_SIZE`, and shared compression constants from `zstd_compress_internal.h`.

## Control Flow
Callers choose between raw/RLE helpers for known special cases or call `ZSTD_compressLiterals()` with source bytes, destination capacity, aligned entropy workspace, previous and next HUF table state, strategy, literal-compression controls, uncompressible-input hint, and BMI2 flag.

## State and Persistence
The header owns no state. Its API makes state movement explicit through `prevHuf` and `nextHuf`, allowing block encoders to preserve repeatable Huffman tables across blocks and roll back when compression falls back to raw literals.

## Dependencies and Integration Points
This header is included by `zstd_compress_literals.c` and `zstd_compress_superblock.c`. It bridges literal payload encoding with the entropy state defined in the internal compressor header.

## Risks
The contracts documented here are important: the entropy workspace must be 4-byte aligned and at least `HUF_WORKSPACE_SIZE`, RLE input must contain one repeated byte, and RLE destination capacity must be at least four bytes. Violating these assumptions is mostly guarded by assertions, not robust runtime checks.

## Test Signals
Compile coverage should include all users of the header. Runtime tests should verify the documented preconditions through normal block encoding, superblock subblock encoding, raw fallback, RLE literals, and repeated HUF table reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.h -->
