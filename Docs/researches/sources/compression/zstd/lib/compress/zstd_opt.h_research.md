# sources/compression/zstd/lib/compress/zstd_opt.h

## Purpose
`zstd_opt.h` declares the internal interface for Zstd optimal binary-tree compressors and dictionary tree loading.

## Important APIs, Types, And Functions
The header declares `ZSTD_updateTree()` when any binary-tree strategy requires dictionary content loading. It declares `btopt`, `btultra`, and `btultra2` block compressors, including dictionary-match-state and external-dictionary variants where supported. It maps `ZSTD_COMPRESSBLOCK_BTOPT`, `ZSTD_COMPRESSBLOCK_BTULTRA`, and related macros to real functions or `NULL` under build exclusion flags.

## Control Flow
There is no runtime control flow. Preprocessor guards define the available optimal-parser surface. `btultra2` is intentionally only declared for no-dictionary mode because its two-pass first-block optimization is not meant for dictionaries.

## State And Persistence
The header owns no state. Its functions operate on `ZSTD_MatchState_t`, `SeqStore_t`, and caller-provided repcode arrays, mutating in-memory match and parser state in the implementation.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` and is consumed by compressor-selection and dictionary-loading code. It is implemented by `zstd_opt.c` and coordinates with compile-time compressor exclusion settings.

## Risks
Mismatched guards can lead to unresolved symbols or missing strategy dispatch. Adding dictionary variants for `btultra2` would violate the implementation contract unless the two-pass state rewind is redesigned.

## Test Signals
Compile matrix tests with `ZSTD_EXCLUDE_BTOPT_BLOCK_COMPRESSOR` and `ZSTD_EXCLUDE_BTULTRA_BLOCK_COMPRESSOR` are primary. Runtime tests should confirm high compression levels select the intended function pointers and dictionary loading still invokes `ZSTD_updateTree()` when needed.
