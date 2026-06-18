# sources/compression/zstd/lib/common/fse.h

## Purpose
`fse.h` declares the Finite State Entropy codec interface used by zstd for compact entropy coding. It exposes the public-ish compression/decompression routines, static allocation macros, workspace sizing rules, repeat-table state enums, and inlined encoder/decoder state transitions used by FSE and Huffman implementations.

## Important APIs, Types, and Functions
The visible API includes version and bounds helpers (`FSE_versionNumber()`, `FSE_compressBound()`), error helpers, count normalization and serialization (`FSE_normalizeCount()`, `FSE_writeNCount()`, `FSE_readNCount()`/`_bmi2()`), table builders (`FSE_buildCTable()`, `FSE_buildDTable_wksp()`), and table-driven compression/decompression (`FSE_compress_usingCTable()`, `FSE_decompress_wksp_bmi2()`). Static-linking declarations define `FSE_CTable`, `FSE_DTable`, sizing macros such as `FSE_CTABLE_SIZE_U32()`, `FSE_DTABLE_SIZE_U32()`, `FSE_DECOMPRESS_WKSP_SIZE_U32()`, and the `FSE_repeat` enum. Inline building blocks include `FSE_CState_t`, `FSE_DState_t`, `FSE_initCState()`, `FSE_initCState2()`, `FSE_encodeSymbol()`, `FSE_flushCState()`, `FSE_initDState()`, `FSE_decodeSymbol()`, `FSE_decodeSymbolFast()`, `FSE_updateState()`, and `FSE_endOfDState()`.

## Control Flow, State, and Persistence
The header documents FSE's two-phase flow. Compression counts symbols, normalizes counts to a power-of-two table, serializes the normalized counts, builds a CTable, then encodes symbols in reverse decode order into a bitstream. Decompression reads the normalized counts, builds a DTable, initializes one or more DStates from the end-oriented bitstream, and decodes symbols while manually reloading the bit container. Runtime state is caller-owned in CTables, DTables, bitstreams, workspaces, and repeat-table flags; nothing is persisted outside caller buffers.

## Dependencies and Integration Points
It depends on `zstd_deps.h` for standard types and, under `FSE_STATIC_LINKING_ONLY`, on `bitstream.h` and `mem.h`-provided integer types. `fse_decompress.c` implements the workspace decompressor, entropy writer/reader code implements the table serializers, and `huf.h` reuses FSE workspace macros for compact Huffman table header decoding. Zstd sequence and literal entropy paths rely on these contracts for exact workspace sizing and table reuse.

## Risks and Test Signals
Risks center on table/workspace sizing and exact bitstream termination. `FSE_decodeSymbolFast()` is explicitly unsafe unless all decoded symbols consume at least one bit, so the DTable `fastMode` flag must be correct. Changing `FSE_MAX_MEMORY_USAGE`, `FSE_MAX_SYMBOL_VALUE`, or table-log limits can invalidate static allocation assumptions. Good tests exercise round trips with repeated tables, low-probability symbols, high-probability symbols that disable fast mode, BMI2 and non-BMI2 reads, malformed normalized counts, too-small workspaces, and exact input-consumption failures.
