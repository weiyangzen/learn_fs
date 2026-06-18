<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/stats.c -->
# sources/distributed-fs/ceph-client/fs/netfs/stats.c

## Purpose
Defines netfs statistic counters and renders netfs plus FS-Cache statistics through procfs.

## Important APIs, Types, And Functions
Exports `netfs_stats_show()`. Defines atomic counters for read origins, write origins, request/subrequest objects, downloads/cache reads/uploads/cache writes, retry requests/subrequests, writeback lock contention, folio queues, and assorted zero/short/write-stream events.

## Control Flow
No complex control flow. Runtime code increments/decrements counters through `netfs_stat()`/`netfs_stat_d()` in `internal.h`. `netfs_stats_show()` reads counters atomically, prints categorized lines, and then calls `fscache_stats_show()` so the same proc file includes FS-Cache diagnostics.

## State And Persistence
Counters are in-memory diagnostics and reset on module load. They are approximate under concurrency but atomic.

## Dependencies And Integration Points
Depends on seq_file and `internal.h`. Hooked into `/proc/fs/netfs/stats` from `main.c` when stats support is enabled. Many netfs read/write paths update these counters.

## Risks
Stats can become misleading if new code paths skip updates or decrement object counters incorrectly. The printed labels are terse, so mapping between labels and counters should remain documented in code or docs.

## Test Signals
Run representative read/write/cache/retry/writeback workloads and verify counter classes move. Object counters should return to zero after requests/subrequests/folio queues are released.
