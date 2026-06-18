# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress_internal.h

## Purpose
`zstd_decompress_internal.h` defines the internal decompression data model shared by the Zstd decompressor modules. It contains sequence base tables, entropy table storage, decompression stages, dictionary-use policy, and the full `ZSTD_DCtx_s` layout.

## Important APIs, types, and functions
Important constants include `LL_base`, `OF_base`, `OF_bits`, `ML_base`, `ZSTD_BUILD_FSE_TABLE_WKSP_SIZE`, `ZSTD_HUFFDTABLE_CAPACITY_LOG`, and literal-buffer sizing macros. Core types are `ZSTD_seqSymbol_header`, `ZSTD_seqSymbol`, `ZSTD_entropyDTables_t`, `ZSTD_dStage`, `ZSTD_dStreamStage`, `ZSTD_dictUses_e`, `ZSTD_DDictHashSet`, `ZSTD_litLocation_e`, and `struct ZSTD_DCtx_s`. It declares `ZSTD_loadDEntropy` and `ZSTD_checkContinuity`, and provides `ZSTD_DCtx_get_bmi2`.

## Control flow
The header supplies the state machine labels used by frame and stream decompression, but contains no major runtime flow itself. Compile-time BMI2 handling makes `ZSTD_DCtx_get_bmi2` either read `dctx->bmi2` or return zero.

## State and persistence
`ZSTD_DCtx_s` persists all decompressor runtime state: entropy table pointers and storage, Huffman workspace, output continuity pointers, expected frame sizes, block type, stage, entropy reuse flags, checksum state, dictionary references, streaming buffers, output hostage-byte tracking, literal buffers, and optional fuzzing metadata. This state is per-context and reused across frames or streams until reset or freed.

## Dependencies and integration points
It depends on common memory types and Zstd internal constants. It is included by block, frame, dictionary, and streaming decompression code, and it must match the opaque `ZSTD_DCtx` public type expected by `<linux/zstd.h>`.

## Risks and test signals
Risks include layout assumptions across modules, workspace-size mismatches, stale entropy or dictionary pointers after reset, incorrect output-continuity classification, and streaming buffer edge cases around `hostageByte` and `noForwardProgress`. Test signals include context reset/reuse, dictionary switching, checksum validation, static-context allocation bounds, streaming with tiny input/output buffers, and builds with dynamic BMI2 enabled and disabled.
