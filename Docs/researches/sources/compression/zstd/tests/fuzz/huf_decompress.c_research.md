# sources/compression/zstd/tests/fuzz/huf_decompress.c

## Purpose

`huf_decompress.c` fuzzes zstd's internal Huffman table-reading and decompression routines on arbitrary compressed-looking input. It is a crash-resistance target: it does not require successful decompression, but it requires table loading and decompression attempts not to crash or access invalid memory.

## Important APIs And Functions

The entry point is `LLVMFuzzerTestOneInput()`. It exercises `HUF_readDTableX1_wksp()` or `HUF_readDTableX2_wksp()` depending on a fuzzer-selected symbol mode, then calls `HUF_decompress1X_usingDTable()` or `HUF_decompress4X_usingDTable()` depending on a stream-count mode.

It allocates `HUF_DTable` storage with `HUF_DTABLE_SIZE(maxTableLog)` and workspace with `HUF_WORKSPACE_SIZE`. Flags include BMI2 when supported, optimal depth, prefer repeat table, suspect uncompressible, disable assembly, and disable fast paths.

## Control Flow

The fuzz data producer consumes prefix bytes to choose streams, X1/X2 decoding, HUF flags, destination buffer size, and maximum table log. The remaining bytes are treated as the Huffman table/compressed payload. The decoder table's first element is initialized from `maxTableLog` before reading the table.

If table reading fails, control jumps to cleanup. If it succeeds, the target attempts a 1X or 4X decompression into a possibly undersized destination buffer and ignores the return code, because any decompression error is a valid result for arbitrary input.

## State And Persistence

All allocation is per invocation: decode table, workspace, and output buffer are freed before return. CPU feature detection through `ZSTD_cpuid()` is read-only process state.

## Dependencies And Integration Points

This file includes internal zstd headers `common/cpu.h` and `common/huf.h`, plus fuzz helper libraries. It tests the lower-level Huffman decoder used by zstd frame/block decoding, including assembly and BMI2-dependent code paths when available.

## Risks And Edge Cases

Important edges include destination size zero, maximum table log extremes, invalid or truncated table payloads, X2 table-log-too-large conditions, repeated-table flags on non-repeat data, and CPU-dependent fast/assembly paths. The test intentionally ignores decompression errors after a valid table load, so it is not a semantic round-trip check.

## Test Signals

The signal is absence of sanitizer findings and process crashes across table-loading and decompression combinations. Corpus inputs that reach successful table reads are valuable because they drive deeper 1X/4X decode paths.
