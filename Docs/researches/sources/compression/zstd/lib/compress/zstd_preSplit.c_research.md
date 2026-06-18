# sources/compression/zstd/lib/compress/zstd_preSplit.c

## Purpose
`zstd_preSplit.c` implements a heuristic for splitting a full 128 KiB block when the beginning and end appear statistically different. It is a pre-compression block boundary detector, not a compressor.

## Important APIs, Types, And Functions
The exported function is `ZSTD_splitBlock()`. Internal types are `Fingerprint` and `FPStats`, which store sampled hash-event histograms. Important helpers are `hash2()`, `initStats()`, generated `ZSTD_recordFingerprint_*()` functions for different sampling rates, `fpDistance()`, `compareFingerprints()`, `mergeEvents()`, `ZSTD_splitBlock_byChunks()`, and `ZSTD_splitBlock_fromBorders()`.

## Control Flow
Level 0 compares byte histograms from both block borders and a middle segment, returning no split, 32 KiB, 64 KiB, or 96 KiB. Levels 1-4 scan 8 KiB chunks with progressively denser fingerprint sampling and larger hash tables. The scanner accumulates past events, compares the next chunk to the accumulated fingerprint with a decreasing penalty, and returns the first statistically different chunk boundary; otherwise it returns the original block size.

## State And Persistence
The caller provides an aligned workspace of at least `ZSTD_SLIPBLOCK_WORKSPACESIZE`. All histograms live in that workspace for the duration of one call. No persistent state or global mutable state is used.

## Dependencies And Integration Points
The file depends on common compiler/memory/dependency/internal headers, `hist.h`, and `zstd_preSplit.h`. It integrates with higher-level compression code that can decide to split 128 KiB blocks before normal block compression.

## Risks
The function currently asserts a full 128 KiB block and aligned workspace; calling it for smaller blocks or unaligned scratch is invalid. The heuristics are ratio/speed-sensitive and can over-split or miss useful boundaries. Workspace layout is manual in `ZSTD_splitBlock_fromBorders()`, so the header size contract must remain correct if `FPStats` changes.

## Test Signals
Signals include direct tests for all levels on homogeneous data, sharply changing data, and borderline distributions; asserts or error handling for invalid block sizes in debug builds; workspace-alignment tests; and compression-ratio benchmarks to confirm that split decisions improve or at least do not regress target corpora.
