# sources/compression/zstd/lib/compress/zstd_ldm.c

## Purpose
`zstd_ldm.c` implements long-distance matching (LDM). It finds content-defined split points with a gear rolling hash, hashes fixed-length anchors with XXH64, records long raw sequences, and either interleaves them with normal block compression or exposes them as candidates to the optimal parser.

## Important APIs, Types, And Functions
Public functions are `ZSTD_ldm_adjustParameters()`, `ZSTD_ldm_getTableSize()`, `ZSTD_ldm_getMaxNbSeq()`, `ZSTD_ldm_fillHashTable()`, `ZSTD_ldm_generateSequences()`, `ZSTD_ldm_skipSequences()`, `ZSTD_ldm_skipRawSeqStoreBytes()`, and `ZSTD_ldm_blockCompress()`. Internal helpers include `ldmRollingHashState_t`, `ZSTD_ldm_gear_init()`, `ZSTD_ldm_gear_reset()`, `ZSTD_ldm_gear_feed()`, `ZSTD_ldm_insertEntry()`, backward match counters, `ZSTD_ldm_fillFastTables()`, `ZSTD_ldm_generateSequences_internal()`, `ZSTD_ldm_reduceTable()`, and `maybeSplitSequence()`.

## Control Flow
Parameter adjustment fills defaults from normal compression parameters. Sequence generation processes input in up to 1 MiB chunks, performs overflow correction, enforces maximum distance, runs the rolling gear hash to collect split points, hashes each candidate window, prefetches buckets, scans bucket entries with checksum filtering, validates forward and backward matches, emits raw sequences, and inserts new entries. When a long match overlaps future hashed data, the rolling hash is reset and scanning skips ahead. Block compression then consumes raw sequences: optimal strategies receive LDM through `ms->ldmSeqStore`, while faster strategies compress literal gaps with the selected block compressor and explicitly store LDM matches.

## State And Persistence
`ldmState_t` stores the LDM window, hash table, circular bucket offsets, split/candidate scratch buffers, and `loadedDictEnd`. `RawSeqStore_t` persists generated raw sequences across block boundaries using `pos` and `posInSequence`. Normal match-state tables may be caught up before compressing literal regions. No filesystem persistence occurs.

## Dependencies And Integration Points
The file depends on `zstd_ldm.h`, `debug.h`, `xxhash.h`, `zstd_fast.h`, `zstd_double_fast.h`, and `zstd_ldm_geartab.h`. It integrates with `ZSTD_window_update()` invariants, window overflow correction, max-distance enforcement, fast/double-fast table filling, block-compressor selection, and optimal parsing via `ms->ldmSeqStore`.

## Risks
Important risks are raw-sequence capacity exhaustion, off-by-one errors around `minMatchLength`, offset validity after chunk splitting, overflow correction invalidating dictionaries, split matches that cross block boundaries, and external-dictionary backward matching across two segments. LDM can strongly affect ratio and speed, so parameter defaults and gear-mask behavior are regression-sensitive.

## Test Signals
Signals include large-window round trips, multithreaded large-input compression, small and huge chunk boundaries, LDM with dictionaries and external dictionaries, capacity-limit error tests from `ZSTD_ldm_getMaxNbSeq()`, sanitizer tests for two-segment counting, and ratio/speed tracking on sparse repeated data where LDM should help.
