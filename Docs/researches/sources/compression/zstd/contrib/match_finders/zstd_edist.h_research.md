<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/match_finders/zstd_edist.h -->
# sources/compression/zstd/contrib/match_finders/zstd_edist.h

## Purpose
This header exposes the edit-distance match finder API for generating zstd sequences from a dictionary/source pair.

## Important APIs, Types, And Functions
It includes static-linking zstd declarations and declares `ZSTD_eDist_genSequences(ZSTD_Sequence* sequences, const void* dict, size_t dictSize, const void* src, size_t srcSize, int useHeuristics)`.

## Control Flow
Callers provide an output sequence buffer and two byte ranges. The implementation computes matching regions and returns the number of generated sequences; enabling heuristics allows faster but potentially non-optimal match scripts.

## State And Persistence
The header defines no state. All state is owned by the implementation call.

## Dependencies And Integration Points
It depends on zstd's static sequence API. It is intended to plug into zstd experimental external sequence workflows and research match-finder comparisons.

## Risks
The function contract does not declare output buffer capacity, so callers must know how much space to provide. The API is experimental and tied to static zstd internals.

## Test Signals
Expected tests should compare generated sequences for known inputs, validate compression with external sequences, and run with heuristics both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/match_finders/zstd_edist.h -->
