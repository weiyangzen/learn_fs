# sources/compression/zstd/lib/common/zstd_internal.h

## Purpose
`zstd_internal.h` contains shared internal definitions that must match across compression, decompression, dictionary building, benchmarks, and tests. It defines frame/block constants, entropy coding tables, repeated-offset defaults, copy helpers, workspace heuristics, private declarations, and CPU feature dispatch helpers.

## Important APIs, Types, and Functions
Important constants include block and frame header sizes, frame checksum size, minimum match size, literal/FSE alphabet limits, default normalized LL/ML/OF tables, `ZSTD_MAX_HUF_HEADER_SIZE`, and `ZSTD_MAX_FSE_HEADERS_SIZE`. Types include `blockType_e`, `SymbolEncodingType_e`, `ZSTD_overlap_e`, `ZSTD_bufferMode_e`, `ZSTD_frameSizeInfo`, and `blockProperties_t`. Inline helpers include `ZSTD_copy8()`, `ZSTD_copy16()`, `ZSTD_wildcopy()`, `ZSTD_limitCopy()`, and `ZSTD_cpuSupportsBmi2()`. Private declarations expose `ZSTD_invalidateRepCodes()`, `ZSTD_getcBlockSize()`, and `ZSTD_decodeSeqHeaders()`.

## Control Flow, State, and Persistence
Most state is static constant lookup data. `ZSTD_wildcopy()` is the main behavioral helper: it copies in 16-byte chunks when buffers are safely separated and falls back to repeated 8-byte copies for short offset overlap where source precedes destination. It may intentionally overread/overwrite up to `WILDCOPY_OVERLENGTH`, so callers must reserve slack. `ZSTD_cpuSupportsBmi2()` probes CPUID dynamically and returns whether BMI1/BMI2 dispatch is available.

## Dependencies and Integration Points
The header pulls in compiler, CPU, memory, debug, public zstd, FSE, HUF, xxhash, and optional tracing definitions. Compression code consumes default FSE norms and copy helpers; decompression uses block parsing types and wildcopy; zstdmt/adaptive compression reach `ZSTD_invalidateRepCodes()`; fullbench uses block-size and sequence-header declarations.

## Risks and Test Signals
Risks are high because constants are format-critical. Changing LL/ML/OF defaults, block header sizes, or field sizes can break frame compatibility. `ZSTD_wildcopy()` requires precise caller preconditions around overlap and output slack; sanitizer tests should cover short offsets, vectorized paths, and boundary slack. BMI2 dispatch should be tested on forced-default and BMI2-capable builds.
