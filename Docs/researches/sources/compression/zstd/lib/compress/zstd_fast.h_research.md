# sources/compression/zstd/lib/compress/zstd_fast.h

## Purpose
Declares the private fast block compressor API for zstd. It exposes hash-table filling and the three fast compressor variants used by the block compressor dispatcher.

## Important APIs, Types, And Functions
The header declares `ZSTD_fillHashTable()`, `ZSTD_compressBlock_fast()`, `ZSTD_compressBlock_fast_dictMatchState()`, and `ZSTD_compressBlock_fast_extDict()`. All compression functions share the `ZSTD_BlockCompressor_f`-style signature with `ZSTD_MatchState_t`, `SeqStore_t`, repeat offsets, source pointer, and source size.

## Control Flow
The header is declarative. Callers fill tables for a CCtx or CDict with `ZSTD_fillHashTable()`, then select the appropriate compression variant based on dictionary mode: no dictionary, attached dictionary match-state, or external dictionary.

## State And Persistence
No state is stored in the header. The declared functions mutate caller-owned match-state tables, sequence store, and repeat-code history.

## Dependencies And Integration Points
It includes common `mem.h` for `U32` and `zstd_compress_internal.h` for compression-private types. It is used by compressor selection and dictionary/table initialization code.

## Risks And Edge Cases
The private signature assumes callers have already initialized window state, hash-table memory, compression parameters, and repeat offsets. Selecting the wrong variant for the active dictionary mode can produce invalid references.

## Test Signals
Compile coverage plus compression round trips for all fast dictionary modes validate the interface. Dispatcher tests should confirm `ZSTD_fast` selects these functions under the expected parameter combinations.
