# sources/compression/zstd/lib/compress/zstd_compress_literals.c

## Purpose
Implements zstd literals-section encoding for raw, RLE, compressed, and repeat-Huffman modes. It decides when literal compression is worthwhile, builds the literals-section header, invokes Huffman compression with repeat-table support, and falls back to raw literals when compression is disabled, too small, unprofitable, or fails.

## Important APIs, Types, And Functions
`ZSTD_noCompressLiterals()` writes a raw literals block with a 1, 2, or 3 byte literals header and copies the source bytes. `ZSTD_compressRleLiteralsBlock()` writes an RLE literals block when all literals are identical. `ZSTD_compressLiterals()` is the main exported function for block compression and accepts destination capacity, source literals, entropy workspace, previous/next Huffman tables, compression strategy, literal-compression disabling, incompressibility suspicion, and BMI2 flags.

Internal helpers include `allBytesIdentical()` and `ZSTD_minLiteralsToCompress()`. Debug builds can log a hexadecimal literal listing through `showHexa()`.

## Control Flow
`ZSTD_compressLiterals()` first copies `prevHuf` into `nextHuf` on the assumption that the previous Huffman table may be reused. If literal compression is disabled, or if the source size is below a strategy- and repeat-mode-dependent threshold, it emits raw literals. Otherwise it reserves the literals header size, configures Huffman flags (`HUF_flags_bmi2`, repeat preference for low strategies, optimal depth for high strategies, and suspect-uncompressible sampling), and calls either `HUF_compress1X_repeat()` for small/single-stream cases or `HUF_compress4X_repeat()`.

After Huffman compression it checks minimum gain with `ZSTD_minGain()`. Failed compression, zero output, errors, or insufficient gain cause the function to restore `nextHuf` from `prevHuf` and emit raw literals. A one-byte Huffman result is treated as a possible single-symbol alphabet; when confirmed, it emits an RLE literals block. Successful new-table compression marks `nextHuf->repeatMode = HUF_repeat_check`; repeat mode writes a `set_repeat` header. The final header encodes type, one-stream/four-stream selector, decompressed literal size, and compressed literal size using 3, 4, or 5 bytes.

## State And Persistence
The persistent state is the Huffman repeat table. `prevHuf` is read, `nextHuf` is tentatively initialized from it, and `nextHuf` either remains a reused table, becomes a freshly built table pending repeat validation, or is restored on fallback. No file/global state is mutated. The entropy workspace must be 4-byte aligned and large enough for `HUF_WORKSPACE_SIZE`.

## Dependencies And Integration Points
This file includes `zstd_compress_literals.h`, which brings in compression internals and Huffman table types. It depends on common helpers for little-endian writes, bounded errors, debug logging, `ZSTD_minGain()`, and Huffman APIs from the common entropy layer. It is used by the regular block compressor and by superblock sub-block compression for literal sections.

## Risks And Edge Cases
Header sizing is sensitive to literal and compressed sizes; wrong thresholds corrupt the literals section. The RLE path asserts that all bytes are identical and that `dstCapacity >= 4`, so callers must satisfy the documented preconditions. The `cLitSize == 1` ambiguity is deliberately handled because it can mean either single-symbol alphabet or a legitimate one-byte compressed stream for tiny inputs. Fallback must restore `nextHuf`, or later repeat-mode decisions can reference a table that was never emitted.

## Test Signals
Round-trip tests should cover raw, RLE, compressed, and repeat literals; tiny inputs below threshold; exactly 31/32, 4095/4096, 1 KB, and 16 KB header boundary sizes; disabled literal compression; incompressible data; single-symbol data; and dictionary/repeat-table reuse across adjacent blocks. Differential tests should compare BMI2 and non-BMI2 outputs for decodability.
