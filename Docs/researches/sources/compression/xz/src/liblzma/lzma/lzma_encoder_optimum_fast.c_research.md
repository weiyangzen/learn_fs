# sources/compression/xz/src/liblzma/lzma/lzma_encoder_optimum_fast.c

## Purpose
Implements the fast greedy-ish match selector for LZMA encoder fast mode. It trades compression ratio for speed by using heuristics over current and next matches instead of full dynamic programming.

## Important APIs, Types, And Functions
- `change_pair()` compares whether a longer-distance candidate is worthwhile relative to a smaller distance.
- `lzma_lzma_optimum_fast()` returns the next `back_res` and `len_res` symbol decision, using match finder results, repeat distances, and lookahead.

## Control Flow
The function obtains current matches with `mf_find()` unless one byte of lookahead is already cached. It rejects matches when fewer than two bytes are available. It checks the four repeat distances first; any repeat match reaching `nice_len` is emitted immediately. A normal match reaching `nice_len` is also emitted immediately. Otherwise it trims suspicious two-byte or distance-expensive matches, prefers repeat matches when close enough to the normal match length, and may encode a literal if the next position has a better match or if a repeat at the next byte would be better. If no heuristic rejects the current normal match, it emits it and skips the remaining matched bytes.

## State And Persistence
Uses and updates match-finder lookahead via `mf_find()`/`mf_skip()`. It stores `coder->longest_match_length` and `coder->matches_count` when it probes the next byte and returns a literal. It reads `coder->reps` but repeat-distance ordering is updated later by `encode_symbol()`.

## Dependencies And Integration Points
Depends on `lzma_encoder_private.h`, `memcmplen.h`, match finder APIs, and `not_equal_16()`. Called only from `lzma_lzma_encode()` when `coder->fast_mode` is true.

## Risks
Heuristic thresholds influence compression ratio and speed. Incorrect `mf_skip()` counts desynchronize `read_ahead`. The cached next-byte match path assumes dictionary buffers are stable between `mf_find()` calls. Two-byte match rejection is distance-sensitive and can affect compatibility only through compression ratio, not decompression correctness.

## Test Signals
Fast-mode round trips at levels 0-3, tiny buffers, inputs with repeated short distances, long-distance two-byte matches, and one-byte lookahead paths should be covered. Compression-ratio benchmarks are useful regression signals for heuristic changes.
