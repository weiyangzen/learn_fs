# sources/compression/zstd/tests/fuzz/huf_round_trip.c

## Purpose

`huf_round_trip.c` fuzzes zstd's internal Huffman compression/decompression pipeline by building a Huffman table from the input, compressing with that table, decompressing with a matching table, and asserting byte-for-byte round-trip correctness.

## Important APIs And Functions

`adjustTableLog()` computes a valid minimum table log for the observed alphabet size using `ZSTD_highbit32()`. The fuzzer entry point calls `HIST_count()`, `HUF_optimalTableLog()`, `HUF_buildCTable_wksp()`, `HUF_writeCTable_wksp()`, `HUF_readDTableX1_wksp()`, `HUF_readDTableX2_wksp()`, `HUF_compress1X_usingCTable()`, `HUF_compress4X_usingCTable()`, and the matching `HUF_decompress*()` routines.

It uses internal constants such as `HUF_WORKSPACE_SIZE`, `HUF_CTABLE_SIZE()`, `HUF_DTABLE_SIZE()`, and `HUF_TABLELOG_MAX`, plus fuzz-selected HUF flags.

## Control Flow

The producer selects stream mode, X1/X2 table read mode, flags, compressed buffer size, and a starting table log. The source payload is capped at 256 KiB. Inputs of size zero/one and RLE-only inputs are skipped because they do not exercise the normal HUF table path.

The harness counts symbols, adjusts table log upward when needed, builds and writes a compression table, reads a decompression table, then compresses using either 1X or 4X. If compression returns zero, the data was not compressed and no round-trip check is performed. Otherwise, decompression must succeed, produce the original size, and match the input via `FUZZ_memcmp()`.

## State And Persistence

All buffers and tables are per input. The only environmental state is CPU feature detection for BMI2 selection. No global context is preserved.

## Dependencies And Integration Points

This target depends on zstd internal histogram, Huffman, CPU, and bit helper headers. It covers table construction and encode/decode implementation used by zstd's literal compression layer, including both one-stream and four-stream variants.

## Risks And Edge Cases

The fuzz target stresses undersized compressed buffers, minimum table-log calculations for non-power-of-two alphabets, X2 decoder fallback to X1 on `tableLog_tooLarge`, RLE/uncompressible cases, and flags that change table depth or fast/assembly paths. Assertions in `adjustTableLog()` assume the computed minimum table log is at most 9 for the byte alphabet cases it sees.

## Test Signals

Any mismatch, decompression-size error, unexpected zstd error, or sanitizer failure is a high-value bug signal. Useful corpus inputs should cover sparse alphabets, near-full 256-symbol alphabets, data near the 256 KiB cap, and compressible versus deliberately uncompressible distributions.
