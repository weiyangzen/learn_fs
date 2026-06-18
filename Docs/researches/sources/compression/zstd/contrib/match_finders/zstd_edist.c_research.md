<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/match_finders/zstd_edist.c -->
# sources/compression/zstd/contrib/match_finders/zstd_edist.c

## Purpose
This file implements an edit-distance-based external match finder that converts similarities between a dictionary and source into zstd `ZSTD_Sequence` entries.

## Important APIs, Types, And Functions
The public entry is `ZSTD_eDist_genSequences`. Internal state types include `ZSTD_eDist_state`, `ZSTD_eDist_match`, and `ZSTD_eDist_partition`. Important helpers are `ZSTD_eDist_diag`, `ZSTD_eDist_compare`, `ZSTD_eDist_insertMatch`, `ZSTD_eDist_combineMatches`, `ZSTD_eDist_convertMatchesToSequences`, Hamming/Levenshtein distance helpers, and validation code.

## Control Flow
`ZSTD_eDist_genSequences` allocates diagonal and match buffers, recursively compares dictionary/source ranges via Myers-style forward/backward diagonals, records matching runs, optionally applies heuristics for expensive regions, sorts/combines contiguous matches, and emits zstd sequences with offsets/literal lengths.

## State And Persistence
State is per-call heap memory allocated through zstd custom memory macros and freed before return. No persistent index is retained.

## Dependencies And Integration Points
It depends on `zstd_edist.h`, `mem.h`, zstd sequence definitions, and `qsort`. It integrates with zstd's external sequence producer API for experimental match-finder research.

## Risks
Worst-case edit-distance work is expensive; heuristics trade optimality for speed. Buffer allocation uses `srcSize`/diagonal counts and lacks broad defensive reporting. Sequence conversion must preserve valid offsets into the dictionary/source.

## Test Signals
There is no direct test in this subset. Indirect signals would come from external sequence producer users validating compression correctness and from internal assertions when enabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/match_finders/zstd_edist.c -->
