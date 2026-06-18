# sources/distributed-fs/ceph-client/lib/zstd/compress/clevels.h

## Purpose
`clevels.h` provides the static table mapping Zstd compression levels to `ZSTD_compressionParameters`. It is the policy table that selects window, chain, hash, search, minimum match, target length, and strategy defaults based on compression level and source-size class.

## Important Data
`ZSTD_MAX_CLEVEL` is `22`. `ZSTD_defaultCParameters[4][ZSTD_MAX_CLEVEL+1]` contains four source-size bands: default for inputs over 256 KiB, at most 256 KiB, at most 128 KiB, and at most 16 KiB. Each row has an index 0 base for negative levels and levels 1 through 22. Strategies progress from `ZSTD_fast` and `ZSTD_dfast` through greedy/lazy variants to `ZSTD_btopt`, `ZSTD_btultra`, and `ZSTD_btultra2`.

## Control Flow and State
The file has no functions and no mutable state. Runtime parameter selection elsewhere indexes this constant table after choosing the size band and clamping the requested compression level. The `__attribute__((__unused__))` marker suppresses warnings when not all builds use the table directly.

## Dependencies and Integration Points
It includes `<linux/zstd.h>` with `ZSTD_STATIC_LINKING_ONLY` so `ZSTD_compressionParameters` and strategy enums are visible. Compressor context initialization and parameter derivation depend on this table to convert user-facing compression levels into concrete algorithm settings.

## Risks and Test Signals
Risks are parameter drift and out-of-range indexing. If public strategy enums or `ZSTD_compressionParameters` layout changes, the initializer must be updated. Tests should verify level clamping, negative-level base behavior, size-band selection at 16 KiB/128 KiB/256 KiB boundaries, max level 22, and representative compression/decompression round trips at low, medium, and ultra levels.
