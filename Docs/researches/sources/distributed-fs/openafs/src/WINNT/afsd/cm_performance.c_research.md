# sources/distributed-fs/openafs/src/WINNT/afsd/cm_performance.c

## Purpose
`cm_performance.c` implements an optional performance-tuning collector for the Windows cache manager. It builds a FID-keyed statistics table from scache, volume, and buffer state, then appends aggregate cache usage summaries to `afsd_performance.log` under `%TEMP%` or the Windows directory.

## Important APIs and functions
- `nearest_prime()` chooses a hash-table size near the requested value using a simple sieve.
- `cm_PerformanceGetNew()` allocates `cm_fid_stats_t` objects from never-freed 32 KiB blocks.
- `cm_PerformanceInsertToHashTable()` inserts a FID-stat object by `fid.hash`.
- `cm_PerformanceAddSCache()` snapshots one non-deleted `cm_scache_t` into a stats entry, including file length/type, read-only flags, and callback state.
- `cm_PerformanceTuningInit()` allocates the stats hash table, scans all scache entries, all volumes, and all valid buffers, and prints the first report.
- `cm_PerformanceTuningCheck()` refreshes existing stats state, discovers new scache/volume entries, recounts valid buffers, and prints a report.
- `cm_PerformancePrintReport()` computes aggregate counts by volume class, scache/volume/buffer presence, callback presence, file type, and file-size bucket.

## Control flow
Initialization sizes the hash table from `cm_data.stats / 3`, walks `cm_data.scacheHashTablep`, then `cm_data.allVolumesp`, then `cm_data.buf_allp`. During scans it drops global locks before taking per-object locks or calling lookup helpers, then reacquires the global lock. Buffer accounting validates a buffer with `cm_FindSCache()` and `cm_HaveBuffer()` before incrementing the FID's `buffers` count. Each run ends by printing a single appended text block.

## State and persistence behavior
The module owns static `fidStatsHashTablep` and `fidStatsHashTableSize`. Individual `cm_fid_stats_t` records are intentionally never freed. Persistent output is only the appended performance log; no cache-manager state is saved from these statistics. Refreshes clear transient flags and counts while preserving RO/PURERO classification.

## Dependencies and integration points
It depends on `cm_data`, `cm_scacheLock`, `cm_volumeLock`, `buf_globalLock`, `cm_FindSCache`, `cm_HaveBuffer`, `cm_HaveCallback`, `cm_SetFid`, `cm_FidCmp`, `cm_ReleaseSCache`, and Windows file APIs (`GetEnvironmentVariable`, `CreateFile`, `WriteFile`). It is diagnostic and tuning-oriented rather than part of core cache correctness.

## Risks and edge cases
- `cm_PerformanceTuningCheck()` hashes `scp->fid` but compares `cm_FidCmp(&fid, &statp->fid)` in the scache loop; `fid` is not initialized in that path. This can prevent existing stat records from matching and create duplicate or incorrect entries.
- `nearest_prime()` loops until `malloc` succeeds and never handles permanent allocation failure.
- `cm_PerformanceGetNew()` is explicitly not thread-safe and assumes only one caller thread.
- The log file can grow without bounds.
- The hash table size can be zero if `cm_data.stats` is very small and allocation fallback is not reached safely.

## Test signals
Tests should inspect report buckets after controlled creation of RW/RO/BACK volume roots, scache entries with/without callbacks, deleted scaches, valid and invalid buffers, and large file lengths. Regression coverage should specifically exercise `cm_PerformanceTuningCheck()` with an existing scache stats record to catch the uninitialized-FID comparison.
