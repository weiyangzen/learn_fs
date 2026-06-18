# sources/compression/zstd/lib/decompress/huf_decompress.c

## Purpose
Implements Huffman decompression for zstd/FSE literals. It builds X1 and X2 decoding tables from serialized Huffman weights, selects an appropriate decoder, handles single-stream and four-stream compressed layouts, provides fast 64-bit little-endian decode loops with optional BMI2/assembly acceleration, and falls back to portable bitstream decoders when fast-loop preconditions are not met.

## Important APIs, Types, And Functions
The key public/internal entry points are `HUF_readDTableX1_wksp()`, `HUF_readDTableX2_wksp()`, `HUF_selectDecoder()`, `HUF_decompress1X_DCtx_wksp()`, `HUF_decompress1X_usingDTable()`, `HUF_decompress1X1_DCtx_wksp()`, `HUF_decompress1X2_DCtx_wksp()`, `HUF_decompress4X_usingDTable()`, and `HUF_decompress4X_hufOnly_wksp()`. Force macros can compile only X1 or only X2 decoder paths.

`DTableDesc` overlays the first `HUF_DTable` word and carries max table log, table type, and active table log. X1 table entries are `HUF_DEltX1 { nbBits, byte }`, decoding one output symbol per lookup. X2 entries are `HUF_DEltX2 { sequence, nbBits, length }`, decoding one or two symbols per lookup. `HUF_DecompressFastArgs` is the shared C/assembly contract for fast 4-stream loops: it stores four input pointers, four output pointers, four bit containers, DTable pointer, input lower bound, output end, and stream ends.

Fast-loop helpers include `HUF_DecompressFastArgs_init()`, `HUF_initFastDStream()`, `HUF_initRemainingDStream()`, `HUF_decompress4X1_usingDTable_internal_fast()`, and `HUF_decompress4X2_usingDTable_internal_fast()`. Portable decoders are built around `BIT_DStream_t`, `BIT_initDStream()`, `BIT_reloadDStream()`, and `BIT_endOfDStream()`.

## Control Flow
For compressed streams that include a Huffman table, the DCtx workspace wrappers first read table weights through `HUF_readStats_wksp()`, build either an X1 or X2 DTable, advance past the table header, and decode the remaining payload. For prebuilt tables, `HUF_decompress1X_usingDTable()` and `HUF_decompress4X_usingDTable()` inspect `DTableDesc.tableType` and route to the matching X1/X2 implementation.

X1 table building optionally rescales weights up to the fast decoder table log, computes rank starts and sorted symbols, and fills repeated table ranges in weight order with specialized loops for lengths 1, 2, 4, 8, and larger. X2 table building sorts symbols by weight, constructs rank value columns for second-level decoding, and fills entries that can emit either one symbol or a two-symbol sequence.

Single-stream decode initializes one bitstream and decodes until the requested output size is reached, then verifies end-of-stream. Four-stream decode reads a 6-byte jump table, splits compressed input into four independent streams, divides output into four nearly equal segments, decodes all streams in lockstep when possible, finishes each stream individually, and verifies that each bitstream ended exactly.

The fast 4-stream path is attempted only for 64-bit little-endian targets, non-empty output, source sizes large enough for four 8-byte bit containers, table log `HUF_DECODER_FAST_TABLELOG`, and output segments large enough to benefit. If init returns zero, the implementation uses the portable fallback. With dynamic BMI2, BMI2-specific wrappers are called only when flags say the CPU supports it; assembly is selected unless disabled by flags and when `ZSTD_ENABLE_ASM_X86_64_BMI2` conditions are met.

## State And Persistence
The file persists no heap state. Decode tables are caller-owned `HUF_DTable` buffers. Temporary table-building state lives in caller-provided workspaces (`HUF_ReadDTableX1_Workspace`, `HUF_ReadDTableX2_Workspace`). Fast-loop state is stored in stack-local `HUF_DecompressFastArgs` and written back from C or assembly loops before finishing through portable bitstream code.

## Dependencies And Integration Points
Dependencies include zstd common memory/dependency wrappers, compiler attributes, bitstream primitives, FSE/HUF table formats, error macros, zstd internal constants, and bit utilities such as high-bit and trailing-zero counts. The amd64 assembly file provides optional implementations of `HUF_decompress4X1_usingDTable_internal_fast_asm_loop()` and `HUF_decompress4X2_usingDTable_internal_fast_asm_loop()` using the exact `HUF_DecompressFastArgs` field layout.

This file integrates into zstd decompression literal-block handling through `huf.h` declarations. It must accept special encodings where `cSrcSize == dstSize` means uncompressed literals and `cSrcSize == 1` means RLE in the one-stream wrapper.

## Risks And Edge Cases
The highest risks are bounds errors in four-stream split handling and fast-loop state reconstruction. Jump table lengths can overflow or produce stream ranges shorter than the fast path expects; these are guarded by length checks but remain critical fuzz targets. The fast loop relies on table log 11, little-endian 64-bit loads, monotonic input pointers, and output segment limits; mismatches must cleanly return zero or corruption errors.

X2 decoding has tricky final-symbol behavior because a table entry may contain two symbols when only one byte remains. `HUF_decodeLastSymbolX2()` intentionally clamps bit consumption in this case. Table construction also has dense rank arithmetic; off-by-one errors in `rankStart`, `rankVal`, or rescaling can create wrong decodes that may only appear with unusual symbol distributions.

Compile-time force flags, dynamic BMI2, static BMI2, `HUF_flags_disableAsm`, and `HUF_flags_disableFast` create many dispatch combinations. The assembly contract is fragile because changing `HUF_DecompressFastArgs` layout or table entry packing without updating assembly breaks accelerated builds.

## Test Signals
Tests should cover one-stream and four-stream blocks, X1 and X2 selected by `HUF_selectDecoder()`, prebuilt-DTable decode, table-read workspace size failures, uncompressed/RLE shortcuts, tiny outputs, malformed jump tables, truncated streams, large 128 KB literal blocks, and randomized valid Huffman distributions. Matrix coverage should include fast enabled/disabled, assembly enabled/disabled, dynamic BMI2 on/off, forced X1/X2 builds, 32-bit builds where the fast path must be bypassed, big-endian simulation if available, and fuzzing of serialized Huffman headers.
