# sources/compression/zstd/lib/compress/zstd_lazy.h

## Purpose
`zstd_lazy.h` declares the public-internal interface for Zstd's greedy, lazy, lazy2, and btlazy2 block compressor implementations and their dictionary-specific variants.

## Important APIs, Types, And Functions
The header defines `ZSTD_LAZY_DDSS_BUCKET_LOG` for dedicated dictionary search buckets and `ZSTD_ROW_HASH_TAG_BITS` for row-match tag filtering. Shared helpers include `ZSTD_insertAndFindFirstIndex()`, `ZSTD_row_update()`, `ZSTD_dedicatedDictSearch_lazy_loadDictionary()`, and `ZSTD_preserveUnsortedMark()`. It declares block compressor entry points for no dictionary, `dictMatchState`, dedicated dictionary search, external dictionary, and row-hash variants, then maps `ZSTD_COMPRESSBLOCK_*` macros either to real functions or `NULL` when excluded at build time.

## Control Flow
There is no runtime control flow. Compile-time `ZSTD_EXCLUDE_*_BLOCK_COMPRESSOR` guards determine which strategies are available. The central compressor selection layer can use the macros without separately testing every exclusion flag.

## State And Persistence
The header owns no state. Its declarations operate on caller-owned `ZSTD_MatchState_t`, `SeqStore_t`, and repcode arrays. Constants affect the shape of hash/tag tables allocated and maintained elsewhere.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` for match-state, sequence-store, repcode, and integer types. It integrates with `zstd_lazy.c`, dictionary loading code, match-state reduction logic, and block-compressor selection in the compression pipeline.

## Risks
Prototype or macro mismatches here break strategy dispatch broadly. The exclusion macros must stay synchronized with implementation guards, or a build can expose unavailable functions or hide available ones. Constants are table-layout contracts; changing them requires auditing allocation, row search, and dedicated dictionary search code.

## Test Signals
Compile-only matrix coverage with each `ZSTD_EXCLUDE_*` option is important. Runtime signals are that selected compression levels still resolve to the intended block compressor and that dictionary-loading paths can call the helper declarations without link failures.
