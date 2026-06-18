# sources/compression/zstd/lib/compress/zstd_double_fast.c

## Purpose
Implements zstd's double-fast block compressor. It uses two hash tables, a long 8-byte hash and a shorter min-match hash, to find better matches than the single-table fast compressor while keeping a speed-oriented parse. It provides no-dictionary, attached dictionary match-state, and external-dictionary variants, plus dictionary table-fill helpers.

## Important APIs, Types, And Functions
Exported functions are `ZSTD_fillDoubleHashTable()`, `ZSTD_compressBlock_doubleFast()`, `ZSTD_compressBlock_doubleFast_dictMatchState()`, and `ZSTD_compressBlock_doubleFast_extDict()`. Static fill helpers specialize CDict table filling with short-cache tagged indices and CCtx table filling with plain indices. Generic compressors are specialized by macro for min-match lengths 4, 5, 6, and 7.

The main implementations are `ZSTD_compressBlock_doubleFast_noDict_generic()`, `ZSTD_compressBlock_doubleFast_dictMatchState_generic()`, and `ZSTD_compressBlock_doubleFast_extDict_generic()`. They use shared helpers from `zstd_compress_internal.h`: `ZSTD_hashPtr()`, `ZSTD_selectAddr()`, `ZSTD_count()`, `ZSTD_count_2segments()`, `ZSTD_storeSeq()`, `ZSTD_getLowestPrefixIndex()`, `ZSTD_getLowestMatchIndex()`, `ZSTD_index_overlap_check()`, and short-cache tag helpers.

## Control Flow
Table fill inserts positions every three bytes. The CDict variant stores packed index/tag entries in both hash tables and may fill additional positions for full loading; the CCtx variant stores plain indices. The long table hashes with match length 8, while the small table hashes with the configured `minMatch`.

The no-dictionary compressor loops from the current anchor. At each candidate it updates both hash tables, checks a repcode at `ip+1`, checks an 8-byte long match, checks a short match, and if a short match is found probes a long match at `ip+1` to prefer the longer parse. It stores sequences, performs complementary insertion around the match end, then consumes immediate repeat-code matches.

The dict-match-state variant checks current-prefix long/short candidates and CDict long/short candidates using packed tags to avoid unnecessary dictionary reads. It translates dictionary indices into the current referential with `dictIndexDelta` and counts matches across dictionary and prefix with `ZSTD_count_2segments()`. The ext-dict variant performs similar two-segment counting against `window.dictBase` and falls back to the no-dict variant when the external dictionary is invalidated by distance.

## State And Persistence
The compressor mutates `ms->hashTable` for long hashes, `ms->chainTable` for small hashes, `seqStore`, and the caller's repeat offsets. It reads match window state, compression parameters, optional `dictMatchState`, and prefetch settings. The final return value is the trailing literal byte count not represented by a sequence; callers later encode those literals. Dictionary tables in CDict mode persist and can use short-cache tags.

## Dependencies And Integration Points
This file is compiled unless `ZSTD_EXCLUDE_DFAST_BLOCK_COMPRESSOR` is defined. It includes `zstd_double_fast.h` and internal compression helpers. The block compressor dispatcher selects these functions for `ZSTD_dfast` strategy modes. It integrates with workspace allocation because `hashTable` and `chainTable` are allocated in `ZSTD_cwksp`, and with entropy encoding through `SeqStore_t`.

## Risks And Edge Cases
The code relies on careful pointer bounds and hash-table update order. Repcode checks at `ip+1` require offset validity and overlap checks, especially for dictionary references. No-dict mode temporarily invalidates repeat offsets outside the prefix and restores saved offsets during cleanup. Dict-match-state mode asserts repcodes are representable and does not support zero-disabling the same way as some no-dict paths.

Choosing between short and long matches affects compression ratio and must preserve decoder-equivalent sequence semantics. Tagged dictionary table entries require correct packing/unpacking and index high bits. Ext-dict mode must count across two segments and choose the correct lower bound for backward extension.

## Test Signals
Round-trip tests should cover `ZSTD_dfast` with minMatch 4-7, no dictionary, prefix, attached CDict, and external dictionary inputs; repeated blocks to validate table reuse and repcode persistence; small blocks near `HASH_READ_SIZE`; long matches versus short-match-at-current plus long-match-at-next decisions; and sanitizer/fuzzer runs for window boundary and non-contiguous input cases.
