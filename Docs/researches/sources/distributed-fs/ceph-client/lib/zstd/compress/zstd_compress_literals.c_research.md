<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.c

## Purpose
`zstd_compress_literals.c` writes the literals section of a compressed block. It handles raw literals, RLE literals, and Huffman-compressed literals while deciding when compression is not worth the cost.

## Important APIs, Types, and Functions
Exported functions are `ZSTD_noCompressLiterals()`, `ZSTD_compressRleLiteralsBlock()`, and `ZSTD_compressLiterals()`. Internal helpers are debug-only `showHexa()`, `allBytesIdentical()`, and `ZSTD_minLiteralsToCompress()`. The code updates `ZSTD_hufCTables_t` repeat mode and CTable state supplied by the caller.

## Control Flow
`ZSTD_compressLiterals()` starts by copying `prevHuf` into `nextHuf`, then immediately emits raw literals when literal compression is disabled or below the strategy-dependent threshold. Otherwise it chooses one-stream Huffman for small input or valid small repeated tables, four-stream Huffman for larger input, sets HUF flags from BMI2/strategy/uncompressible suspicion, and calls `HUF_compress1X_repeat()` or `HUF_compress4X_repeat()`. If the result is zero, an error, or does not beat `ZSTD_minGain()`, the function restores `nextHuf` and emits raw literals. A one-byte HUF result is converted to an RLE literal block when the input really has a single symbol. Successful new-table compression marks `nextHuf->repeatMode = HUF_repeat_check` and writes the literal-section header.

## State and Persistence
The file itself has no persistent global state. It mutates caller-owned entropy state by copying/reusing/refreshing HUF tables and repeat mode. Output persistence is the byte format in `dst`: a variable-width literal section header followed by raw bytes, one RLE byte, or Huffman payload.

## Dependencies and Integration Points
The implementation depends on `zstd_compress_literals.h`, which brings in compression internals, HUF tables, `ZSTD_minGain()`, block constants, `MEM_writeLE*()`, and error macros. It is used by regular block compression and the superblock path; `zstd_compress_superblock.c` also calls the raw and RLE helpers directly when building subblocks from precomputed entropy.

## Risks
Header-size selection is sensitive to literal and compressed sizes. `ZSTD_compressRleLiteralsBlock()` asserts that all bytes are identical and `dstCapacity >= 4`, so callers must honor the contract. The HUF return value `1` has overloaded meaning and requires the explicit identical-byte check. Incorrect repeat-mode restoration on fallback would corrupt later blocks.

## Test Signals
Tests should exercise empty/small/large literals, disabled literal compression, fast-strategy target-length auto-disable behavior, RLE single-symbol blocks, HUF repeat reuse, new HUF table emission, compressed output that expands and falls back to raw, suspect-uncompressible mode, BMI2 and non-BMI2 paths, and destination-too-small errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_compress_literals.c -->
