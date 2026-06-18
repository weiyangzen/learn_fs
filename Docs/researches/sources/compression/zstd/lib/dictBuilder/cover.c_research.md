# sources/compression/zstd/lib/dictBuilder/cover.c

## Purpose
`cover.c` implements zstd's static-linking-only COVER dictionary trainer and the shared "best candidate" selection utilities used by both COVER and FASTCOVER optimization. It builds dictionaries by scoring repeated `d`-byte substrings ("dmers") across training samples, selecting high-value `k`-sized segments by epoch, finalizing selected raw content into a zstd dictionary, and optionally evaluating many parameter candidates against held-out samples.

## Important APIs, Types, And Functions
- `ZDICT_trainFromBuffer_cover()` is the direct COVER training entry point. It validates `ZDICT_cover_params_t`, initializes a `COVER_ctx_t`, builds a raw dictionary, then calls `ZDICT_finalizeDictionary()`.
- `ZDICT_optimizeTrainFromBuffer_cover()` searches candidate `d` and `k` values, optionally using `POOL_ctx`, and returns the best dictionary plus the winning parameters through the caller's `ZDICT_cover_params_t`.
- `COVER_ctx_t` owns the sample pointer, offsets, counts, partial suffix data, dmer frequencies, and dmer-id lookup table for a single `d` value.
- `COVER_map_t` is a fixed-size linear-probing map for the active segment window. It tracks unique dmer occurrences while sliding a segment over an epoch.
- `COVER_buildDictionary()` repeatedly calls `COVER_selectSegment()` over computed epochs, copies selected source segments into the dictionary buffer from the end backward, and stops when the buffer is full or scoring dries up.
- `COVER_checkTotalCompressedSize()` evaluates a finalized dictionary by creating a `ZSTD_CDict`, compressing selected validation samples, and returning dictionary size plus compressed sizes.
- `COVER_best_*()` manages cross-thread selection of the best candidate dictionary. It tracks live jobs with zstd pthread wrappers and stores the candidate with the smallest `totalCompressedSize`.
- `COVER_selectDict()` finalizes raw dictionary content and, when `shrinkDict` is enabled, searches for the smallest dictionary within the configured regression tolerance.

## Control Flow
The direct path validates parameters, sample count, and destination capacity, then calls `COVER_ctx_init()`. Context initialization computes train/test split counts, sample offsets, a partial suffix array over all possible dmers, stable-sorts that array using the platform qsort variant, groups equal dmers, records per-position dmer ids, and reuses the suffix allocation as the frequency table. `COVER_buildDictionary()` computes epochs with `COVER_computeEpochs()`, scans each epoch with a sliding window, selects the highest scoring segment, zeros the frequencies of covered dmers, and appends the chosen segment at the back of the output buffer. The direct entry then finalizes the selected content using entropy tables derived from all samples.

The optimized path chooses default ranges (`d` 6/8, `k` 50..2000, 40 steps, split point 0.75 unless supplied), initializes one context per `d`, and tries each `k`. Each try clones the frequency table, builds a candidate dictionary, calls `COVER_selectDict()`, and reports the result to `COVER_best_finish()`. The parent waits for all jobs for a `d` before destroying that context, then copies the best dictionary to the caller's buffer.

## State And Persistence
All training state is process-local and transient. `COVER_ctx_t` borrows `samplesBuffer` and `samplesSizes`, but owns allocated `offsets`, `dmerAt`, and either `suffix` or `freqs`. Candidate workers own their opaque argument, cloned frequency table, temporary dictionary buffer, active dmer map, and dictionary-selection allocation until cleanup. `COVER_best_t` persists across candidate jobs during optimization and owns a heap copy of the best dictionary until `COVER_best_destroy()`. The only external writes are to caller-provided dictionary buffers and optional progress messages to `stderr`.

## Dependencies And Integration Points
This file depends on zstd common memory, debug, bits, threading, pool, and compression APIs, plus `../zdict.h` and `cover.h`. It calls `ZDICT_finalizeDictionary()` from `zdict.c`, `ZSTD_createCDict()`, `ZSTD_compress_usingCDict()`, and zstd error helpers. `fastcover.c` reuses `COVER_best_t`, `COVER_computeEpochs()`, `COVER_warnOnSmallCorpus()`, `COVER_sum()`, `COVER_selectDict()`, and compression-size evaluation through `cover.h`. Platform integration is sensitive to `qsort_r`/`qsort_s` ABI differences; the C90 fallback uses a global `g_coverCtx`.

## Risks And Edge Cases
- `COVER_map_t` does not resize and can loop indefinitely if undersized; callers size it from `k - d + 1`, so parameter validation is critical.
- The C90 `qsort()` fallback uses global context and is explicitly not reentrant, making concurrent optimized training unsafe on platforms without reentrant sort support.
- Size casts to `U32` and the `COVER_MAX_SAMPLES_SIZE` limit constrain usable corpus sizes; 32-bit builds are capped much lower.
- `splitPoint == 1.0` makes train and test sets both cover all samples in direct training. Optimized training uses a held-out split by default.
- `COVER_selectDict()` copies and re-finalizes dictionary content repeatedly during shrink search; regressions can appear around overlapping buffers and minimum dictionary size.
- In `COVER_best_finish()`, allocation failure while replacing the best dictionary stores a generic error but still decrements live jobs; callers must check `best.compressedSize`.

## Test Signals
Useful coverage includes parameter-boundary tests for `d`, `k`, `splitPoint`, small sample count, and small destination buffers; deterministic training tests on fixed corpora; optimization tests with one and multiple threads; shrink-dictionary tests validating compressed-size regression tolerance; memory-failure or sanitizer runs around candidate cleanup; and platform builds that exercise GNU, Apple, MSVC/C11, and fallback qsort selection.
