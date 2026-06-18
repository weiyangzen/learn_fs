# sources/compression/zstd/lib/dictBuilder/fastcover.c

## Purpose
`fastcover.c` implements zstd's FASTCOVER dictionary trainer, a faster variant of COVER that hashes 6- or 8-byte dmers into a fixed-size frequency table instead of sorting exact dmers. It supports direct training and parameter optimization, reusing shared COVER utilities for epoch computation, dictionary finalization, candidate scoring, and best-result synchronization.

## Important APIs, Types, And Functions
- `ZDICT_trainFromBuffer_fastCover()` trains one FASTCOVER dictionary with supplied `ZDICT_fastCover_params_t`, defaulting `splitPoint` to `1.0`, `f` to `20`, and `accel` to `1`.
- `ZDICT_optimizeTrainFromBuffer_fastCover()` searches `d`, `k`, and fixed `f/accel` settings, optionally in a thread pool, and writes winning FASTCOVER parameters back to the caller.
- `FASTCOVER_ctx_t` stores borrowed samples, owned offsets and frequency table, train/test counts, number of dmers, `d`, `f`, acceleration parameters, and display level.
- `FASTCOVER_accel_t` maps an acceleration level to a percentage of training samples used for finalization and a skip count for frequency collection.
- `FASTCOVER_hashPtrToIndex()` maps a dmer pointer to a `2^f` frequency-table index using zstd internal hash functions.
- `FASTCOVER_computeFrequency()` counts hashed dmers over training samples, applying acceleration skips.
- `FASTCOVER_selectSegment()` scores a sliding `k` segment using hashed dmer frequencies and a `U16` per-segment frequency table to avoid double-counting duplicate hash values inside the active segment.
- `FASTCOVER_buildDictionary()` selects segments by epoch and copies them into the output buffer from the back.

## Control Flow
Direct training validates that `d` is 6 or 8, `k <= maxDictSize`, `d <= k`, `0 < f <= 31`, `splitPoint` is in range, and `accel` is 1..10. Context initialization computes sample offsets and allocates a `2^f` frequency table. Frequency collection walks each training sample while `start + MAX(d, 8) <= sampleEnd`, hashes the current dmer, increments the count, and advances by `skip + 1`. Dictionary construction computes epochs, selects high-score segments, zeros frequencies for selected hashes, and emits raw content into the tail of the destination buffer. The result is finalized with `ZDICT_finalizeDictionary()`, using only the configured fraction of training samples for entropy finalization.

Optimized training defaults split point to 0.75, defaults `d` to trying 6 and 8, `k` to 50..2000 across 40 steps, and launches `FASTCOVER_tryParameters()` jobs. Each job clones the frequency table, builds raw content, calls `COVER_selectDict()`, and submits the result to `COVER_best_finish()`. The parent waits after each `d` value before destroying the shared context.

## State And Persistence
FASTCOVER keeps no persistent state outside caller buffers. The context borrows sample data and owns `offsets` and `freqs`. Each candidate owns cloned frequencies, a temporary dictionary buffer, a `segmentFreqs` array sized to `2^f`, and its opaque data object. `COVER_best_t` owns the winning dictionary copy until destroyed. Progress output goes to `stderr` through local display macros.

## Dependencies And Integration Points
This file depends on zstd common memory, pool, threading, internal compression hash functions from `zstd_compress_internal.h`, public/static dictionary types from `../zdict.h`, and shared COVER helpers from `cover.h`. `zdict.c` uses FASTCOVER optimization as the default implementation behind `ZDICT_trainFromBuffer()`. It integrates with `POOL_ctx` for multi-threaded search and with `ZDICT_finalizeDictionary()`/`COVER_selectDict()` for final dictionary construction and scoring.

## Risks And Edge Cases
- Hash collisions mean FASTCOVER approximates dmer identity; this is intentional but can select different content than exact COVER on collision-heavy corpora or small `f`.
- `segmentFreqs` is `U16`; very large `k` with many repeated hashes can overflow per-segment counts.
- `1 << f` allocations can be very large as `f` approaches 31, even though the parameter is technically valid.
- Direct training sets `splitPoint = 1.0` regardless of user input, so all samples are used for both training/finalization; optimized training honors/defaults a held-out split.
- Acceleration reduces frequency fidelity and finalization sample count; higher levels trade quality for speed.
- `ctx.nbDmers = trainingSamplesSize - MAX(d, sizeof(U64)) + 1` relies on earlier size checks to avoid underflow.

## Test Signals
Useful tests cover `d` restrictions, `f` and `accel` bounds, small sample rejection, deterministic fixed-corpus output, default parameter filling, multi-threaded optimization parity with serial optimization, high-acceleration behavior, and sanitizer checks for large `f` allocations and `segmentFreqs` indexing. End-to-end `ZDICT_trainFromBuffer()` tests also exercise this file because it is the default trainer.
