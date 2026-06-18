# sources/compression/zstd/lib/compress/clevels.h

## Purpose
`clevels.h` stores zstd's pre-defined compression-parameter table. It maps source-size bands and compression levels to `ZSTD_compressionParameters`, providing the baseline policy used when callers request numeric compression levels instead of explicit tuning.

## Important APIs, Types, and Functions
The header defines `ZSTD_MAX_CLEVEL` as `22` and the static `ZSTD_defaultCParameters[4][ZSTD_MAX_CLEVEL+1]` table. Each row entry contains window log, chain log, hash log, search log, minimum match length, target length, and strategy. The four size bands are default for inputs larger than 256 KB, inputs up to 256 KB, inputs up to 128 KB, and inputs up to 16 KB. Entry zero is the base for negative levels.

## Control Flow, State, and Persistence
There is no runtime control flow. The table is read-only static data selected by higher-level parameter selection code based on source size and requested level. Strategies progress from `ZSTD_fast` and `ZSTD_dfast` through greedy/lazy modes to binary-tree optimal modes (`ZSTD_btopt`, `ZSTD_btultra`, `ZSTD_btultra2`) as levels increase.

## Dependencies and Integration Points
The header defines `ZSTD_STATIC_LINKING_ONLY` before including `../zstd.h` to expose `ZSTD_compressionParameters` and strategy enums. Compression context initialization and parameter adjustment code consume this table as the canonical built-in level policy.

## Risks and Test Signals
Changing values affects compression ratio, speed, memory use, and compatibility with published level expectations. Table dimensions must stay aligned with `ZSTD_MAX_CLEVEL`; off-by-one errors would mis-map levels. Test signals include snapshotting parameters for representative levels and sizes, verifying negative-level base behavior, and performance/regression tests for boundary sizes around 16 KB, 128 KB, and 256 KB.
