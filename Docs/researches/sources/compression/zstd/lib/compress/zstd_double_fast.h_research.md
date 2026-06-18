# sources/compression/zstd/lib/compress/zstd_double_fast.h

## Purpose
Declares the private double-fast compressor interface and provides null macros when the double-fast block compressor is excluded at build time.

## Important APIs, Types, And Functions
When enabled, the header declares `ZSTD_fillDoubleHashTable()`, `ZSTD_compressBlock_doubleFast()`, `ZSTD_compressBlock_doubleFast_dictMatchState()`, and `ZSTD_compressBlock_doubleFast_extDict()`. It also defines dispatcher macros `ZSTD_COMPRESSBLOCK_DOUBLEFAST`, `ZSTD_COMPRESSBLOCK_DOUBLEFAST_DICTMATCHSTATE`, and `ZSTD_COMPRESSBLOCK_DOUBLEFAST_EXTDICT`, which become `NULL` if `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR` is set.

## Control Flow
The header is declarative. Compressor selection code can use the macros without conditionalizing every call site on build exclusion.

## State And Persistence
No state is owned here. The declared functions operate on `ZSTD_MatchState_t`, `SeqStore_t`, and repeat-code arrays owned by the caller.

## Dependencies And Integration Points
It includes common memory types and `zstd_compress_internal.h` for match-state and sequence-store definitions. It integrates with the block compressor selector and with CDict/CCtx table-loading code.

## Risks And Edge Cases
Build configurations excluding double-fast must handle the `NULL` macros and avoid selecting those compressors. Signature drift between this header and the implementation would break private compressor dispatch.

## Test Signals
Compile tests with and without `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR`, plus compression tests that select double-fast in all dictionary modes, validate the header contract.
