# File Research: sources/cow-pools/openzfs/module/zfs/spa_stats.c

## Role

`spa_stats.c` implements per-pool observability for the SPA. It creates procfs rolling histories and kstats for recent reads, TXG syncs, `dmu_tx_assign()` latency, multihost protection writes/skips, pool state, pool GUID, and pool-level I/O counters.

The file is controlled by tunables for history lengths. Most history paths are cheap no-ops when the associated history length is zero and the list is empty.

## Read History

The read-history section records recent `arc_read` calls in `spa_read_history_t`: completion time, objset, object, level, block ID, origin buffer, ARC flags, PID, process name, and procfs node ID. `spa_read_history_init()` installs a per-pool `reads` procfs file with a clear callback; `spa_read_history_destroy()` uninstalls and truncates it.

`spa_read_history_add()` skips work when `zfs_read_history` is disabled, and can exclude ARC cache hits unless `zfs_read_history_hits` is enabled. On record creation it captures process identity and bookmark fields, appends to the procfs list under its lock, increments list size, and truncates to the configured maximum.

## TXG History

TXG history records one `spa_txg_history_t` per recent transaction group, including TXG number, current state, bytes/operations read and written, dirty bytes, and timestamps for TXG state transitions through committed.

`spa_txg_history_add()` starts a new TXG record at birth/open time. `spa_txg_history_set()` records a completed state timestamp and increments the stored state. `spa_txg_history_init_io()` captures vdev stats before `spa_sync()`, records the wait-for-sync timestamp, and returns a temporary `txg_stat_t`. `spa_txg_history_fini_io()` captures post-sync vdev stats, records the synced timestamp, calculates read/write byte and op deltas plus dirty bytes, stores them in the TXG history row, and frees the temporary stat object.

The procfs output shows TXG, birth time, compact state character, dirty/read/write counters, and elapsed open/quiesce/wait/sync durations.

## TX Assign Histogram

The `dmu_tx_assign` kstat is a named histogram with 42 power-of-two buckets from 1 ns up to about 2,199 seconds. `spa_tx_assign_init()` allocates and names the buckets under `zfs/<pool>/dmu_tx_assign`. `spa_tx_assign_add_nsecs()` finds the first bucket whose threshold is at least the supplied duration and atomically increments it.

`spa_tx_assign_update()` clears buckets on kstat write and trims trailing zero buckets on read by lowering `ks_ndata` and `ks_data_size`.

## MMP History

The multihost-protection history records attempted MMP writes and skipped-write spans. A `spa_mmp_history_t` stores an ID, TXG, UTC timestamp, MMP delay, vdev GUID/path/label, I/O error, error-start time, and duration.

`spa_mmp_history_add()` appends either a write record or an error/skip record. For skipped writes, `vdev_guid` is reused as a count initialized to one and `error_start` marks the beginning of the skip interval. `spa_mmp_history_set_skip()` updates the duration and increments that count for a matching skip record. `spa_mmp_history_set()` fills in completion error and duration for an issued MMP write.

The procfs output uses a different formatting path for skip records versus normal write records.

## State, GUID, And I/O Kstats

`spa_state_init()` creates a raw no-header kstat named `zfs/<pool>/state` that reports `spa_state_to_name(spa)`. It is intentionally lockless so monitoring can read it as a lightweight heartbeat without invoking `zpool` paths.

`spa_guid_init()` creates a raw no-header kstat named `zfs/<pool>/guid` that reports `spa_guid(spa)`.

The `iostats` named kstat contains counters for manual trim, autotrim, simple trim, ARC reads/writes, and direct reads/writes. `spa_iostats_trim_add()`, `spa_iostats_read_add()`, and `spa_iostats_write_add()` atomically add values to the appropriate counters. A write to the kstat resets the data to `spa_iostats_template`.

## Lifecycle

`spa_stats_init()` initializes read history, TXG history, TX assign histogram, MMP history, state kstat, GUID kstat, and I/O stats for a newly added SPA. `spa_stats_destroy()` tears down I/O stats, state, TX assign histogram, TXG history, read history, MMP history, and GUID.

The file exposes module parameters for read history length, inclusion of read hits, TXG history length, and multihost history length.

## Risks And Invariants

History list operations must hold the procfs list lock while appending, truncating, clearing, or searching. Kstat update paths must preserve the allocated backing data lifetime until deletion.

Most counters are diagnostic, not correctness-critical, but TXG history is used by `txg.c` around state transitions and `spa_sync()` I/O measurement. Missing or reordered calls can make `/proc` output misleading, especially for diagnosing sync latency and pool import or MMP behavior.
