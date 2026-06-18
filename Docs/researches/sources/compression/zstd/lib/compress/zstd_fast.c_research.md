# sources/compression/zstd/lib/compress/zstd_fast.c

## Purpose
Implements zstd's fastest single-hash-table block compressor. It provides table-filling and block parsing for no dictionary, attached dictionary match-state, and external dictionary modes. The parser prioritizes speed through pipelined hash/table/match operations, adaptive skipping, and specialized min-match variants.

## Important APIs, Types, And Functions
Exported functions are `ZSTD_fillHashTable()`, `ZSTD_compressBlock_fast()`, `ZSTD_compressBlock_fast_dictMatchState()`, and `ZSTD_compressBlock_fast_extDict()`. Static fill helpers distinguish CDict tagged-index tables from CCtx plain-index tables. `ZSTD_match4Found_cmov()` and `ZSTD_match4Found_branch()` provide two candidate validation strategies; no-dict mode selects cmov for smaller windows where candidate-in-range is less predictable.

Main generic parsers are `ZSTD_compressBlock_fast_noDict_generic()`, `ZSTD_compressBlock_fast_dictMatchState_generic()`, and `ZSTD_compressBlock_fast_extDict_generic()`. Macro-generated wrappers specialize min-match lengths 4-7 and cmov/branch variants.

## Control Flow
`ZSTD_fillHashTable()` inserts positions every three bytes from `nextToUpdate` to the requested end. CDict filling uses short-cache tag packing and full loading; CCtx filling uses plain hashes and currently asserts fast loading.

The no-dict compressor uses a deliberately pipelined loop over adjacent and stepped positions (`ip0`..`ip3`). It interleaves repcode checks, hash computation, table lookup, table writeback, and match comparison to reduce dependency stalls. When a repcode or normal match is found, it optionally extends backward, counts forward match length, stores a sequence, inserts complementary positions, consumes immediate repeat-code matches, and restarts. It returns the final literal tail size.

The dict-match-state compressor checks current-prefix matches and attached dictionary matches. Dictionary hash entries carry short-cache tags, and dictionary matches are only used in one path when the normal prefix match is invalid to mirror ext-dict parsing behavior. The ext-dict compressor resolves each index against `dictBase` or `base`, counts matches across dictionary and prefix, and falls back to no-dict mode if the external dictionary has been invalidated.

## State And Persistence
The function mutates `ms->hashTable`, `seqStore`, and repeat offsets. It reads `ms->window`, `cParams`, `dictMatchState`, and `prefetchCDictTables`. It updates only the first two repeat offsets directly; the broader repeat-code convention is completed by the shared sequence encoding path. Saved invalid rep offsets are restored during cleanup so cross-block history remains correct even when a repcode cannot be used in the current prefix.

## Dependencies And Integration Points
It includes `zstd_compress_internal.h` and `zstd_fast.h`. The block compressor selector chooses these functions for `ZSTD_fast` strategy modes. It integrates with the workspace-managed hash table, dictionary table loading, window/dictionary validity logic, and later entropy encoding via `SeqStore_t`.

## Risks And Edge Cases
This code is highly performance-tuned and sensitive to instruction ordering. Comments note places where boolean expressions, inline assembly barriers, or writeback order are chosen to influence branch generation and safety. Bounds are guarded by `ilimit = iend - HASH_READ_SIZE`, but many reads intentionally rely on that invariant. Repcode invalidation/restoration at prefix boundaries is subtle. Dict-match-state asserts that repcodes are within dictionary+prefix length and does not support zero-disabled repcodes in the same way as no-dict mode.

Non-contiguous input and ext-dict overlap require correct `prefixStartIndex`, `dictStartIndex`, and `lowLimit` calculations. Short-cache tagged CDict entries must be compared before dictionary memory reads to avoid expensive misses without dropping valid matches.

## Test Signals
Round-trip tests should force `ZSTD_fast` with minMatch 4-7, small and large windows, cmov and branch variants, no dictionary, prefix dictionaries, attached CDicts, external dictionaries, non-contiguous streaming segments, and immediate repeat-code chains. Performance regression tests are also important because many transformations that preserve correctness can hurt the intended fast path.
