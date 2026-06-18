# sources/compression/lz4/lib/lz4hc.h

## Purpose
`lz4hc.h` declares the stable and static-linking-only API for LZ4 high-compression mode. It exposes block compression, streaming compression, dictionary support, and compatibility wrappers for older HC names.

## Important APIs, Types, And Functions
The public constants define the supported level range: `LZ4HC_CLEVEL_MIN`, `LZ4HC_CLEVEL_DEFAULT`, `LZ4HC_CLEVEL_OPT_MIN`, and `LZ4HC_CLEVEL_MAX`. Block APIs include `LZ4_compress_HC()`, `LZ4_sizeofStateHC()`, `LZ4_compress_HC_extStateHC()`, and `LZ4_compress_HC_destSize()`. Streaming APIs use the opaque `LZ4_streamHC_t` and include create/free, reset, dictionary load/save, continue, continue-destSize, and `LZ4_attach_HC_dictionary()`.

## Control Flow
The header itself has no runtime control flow, but its comments define required call order: initialize or create a stream, optionally set the compression level before loading a dictionary, compress blocks with previous data still accessible, save history if prior buffers cannot remain stable, and reset before reusing a stream.

## State, Persistence, And Dependencies
The static-linking section reveals `LZ4HC_CCtx_internal` with hash and chain tables, prefix and dictionary pointers, window limits, compression level, flags, and attached dictionary context. The `LZ4_streamHC_t` union reserves `LZ4_STREAMHC_MINSIZE` bytes for static allocation. State is process memory only.

## Integration Points
The header includes `lz4.h`, shares `LZ4LIB_API` and deprecation machinery, and exposes experimental static APIs when `LZ4_HC_STATIC_LINKING_ONLY` is defined. CLI, fuzzers, and library consumers include this file for HC compression.

## Risks
Static-linking-only layout is explicitly unstable and must not be used for dynamic-library ABI. `LZ4_saveDictHC(NULL, nonzero)` is invalid. Streaming correctness depends on retaining previous input buffers or explicitly saving history. Deprecated functions are preserved but may have degraded behavior.

## Test Signals
Compile tests should cover public and static-linking modes, C and C++ inclusion, deprecated-warning suppression, static allocation through `LZ4_initStreamHC()`, and dictionary attach/load/save flows.
