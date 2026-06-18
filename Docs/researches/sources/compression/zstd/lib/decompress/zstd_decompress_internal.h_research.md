# sources/compression/zstd/lib/decompress/zstd_decompress_internal.h

## Purpose
`zstd_decompress_internal.h` defines shared decompression tables, internal decode types, context state, and helper prototypes used across zstd decompression modules. It is the structural contract between frame decoding, block decoding, dictionary handling, and streaming.

## Important APIs, Types, And Functions
Static base/additional-bit tables `LL_base`, `OF_base`, `OF_bits`, and `ML_base` define sequence symbol interpretation. Key types are `ZSTD_seqSymbol_header`, `ZSTD_seqSymbol`, `ZSTD_entropyDTables_t`, `ZSTD_dStage`, `ZSTD_dStreamStage`, `ZSTD_dictUses_e`, `ZSTD_DDictHashSet`, `ZSTD_litLocation_e`, and the full `struct ZSTD_DCtx_s`. It also defines table/workspace sizing macros, literal extra buffer sizing, `ZSTD_DCtx_get_bmi2()`, and prototypes for `ZSTD_loadDEntropy()` and `ZSTD_checkContinuity()`.

## Control Flow
This header has no executable flow beyond the inline BMI2 accessor. Its enums encode the control-flow states used by `ZSTD_decompressContinue()` and `ZSTD_decompressStream()`: frame header sizing, frame header decode, block header decode, block decompression, last block, checksum, skippable header, skippable payload, stream initialization, header loading, reading, loading, and flushing.

## State And Persistence
`ZSTD_DCtx_s` is the persistent decompression state container. It stores entropy tables and pointers, history boundaries, expected input size, frame parameters, block type, checksum state, dictionary pointers and use policy, multiple-DDict set, streaming buffers and positions, legacy stream state, output-buffer stability data, literal buffers, oversized-buffer tracking, optional fuzzing dictionary bounds, and optional trace context. State persists across streaming calls and selected resets according to `ZSTD_DCtx_reset()` semantics.

## Dependencies And Integration Points
The header depends on common memory and zstd internal constants plus HUF/XXH types pulled through those includes. It is consumed by both decompression C files and by DDict support code. Its layout affects static context sizing, workspace sharing between FSE and HUF table construction, and the public opaque `ZSTD_DCtx`/`ZSTD_DStream` objects declared in `zstd.h`.

## Risks
Layout and sizing changes can break static allocation, table workspace assumptions, or dictionary table reuse. The literal extra buffer size balances memory against safety for split literals. History pointer fields must stay coherent with `ZSTD_checkContinuity()` and external dictionary matching. New fields need reset, copy, size-accounting, and static-workspace consideration.

## Test Signals
Compilation across decompression modules, static DCtx/DStream tests, dictionary round trips, streaming fragmented-input tests, checksum tests, repeated entropy-table tests, and fuzzing builds with sequence assertions all exercise this contract.
