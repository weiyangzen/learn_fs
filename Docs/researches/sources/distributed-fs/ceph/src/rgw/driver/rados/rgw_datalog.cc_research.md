# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog.cc

## Purpose
This file implements the RGW data changes log used by multisite data sync to record bucket shard changes. It supports two generation-aware backing formats, legacy cls log omap and newer cls fifo, plus background tasks that coalesce frequent changes, maintain semaphores for crash recovery, watch other RGWs, synthesize missed log entries, trim old generations, and expose admin semaphore tooling.

## Important APIs, Types, and Functions
`rgw_data_change`, `rgw_data_change_log_entry`, `rgw_data_notify_entry`, and `RGWDataChangesLogInfo` implement dump/decode helpers for log entries, notification entries, and per-shard marker info.

`RGWDataChangesOmap` and `RGWDataChangesFIFO` are concrete `RGWDataChangesBE` backends. Omap stores `cls::log::entry` values with `nlog::add/list/info/trim`; FIFO stores encoded bufferlists through `LazyFIFO`. Both convert backend records to `rgw_data_change_log_entry`, expose `max_marker()`, detect empty generations, and tolerate missing objects as empty where appropriate.

`DataLogBackends` owns generation metadata through `logback_generations` and a map of generation id to backend. Its `list()` walks generations using `cursorgen()` and `gencursor()`, `trim_entries()` trims all generations up to a target generation/cursor, and `trim_generations()` prunes empty non-head generations.

`RGWDataChangesLog` is the service class. Public APIs include `start()`, `add_entry()`, `list_entries()`, `get_info()`, `trim_entries()`, `trim_generations()`, `change_format()`, `mark_modified()`, `read_clear_modified()`, `recover()`, shutdown, and admin semaphore list/reset. Internal helpers include `choose_oid()`, `_get_change()`, `renew_entries()`, `watch_loop()`, `process_notification()`, `synthesize_entries()`, `gather_working_sets()`, and `decrement_sems()`.

## Control Flow
Startup initializes a RADOS ioctx for the zone log pool, initializes the generation metadata object with FIFO as the default backing, and optionally starts renew, watch, and recovery coroutines. If data logging is disabled, the ioctx and backends are still initialized but background logging returns early.

`add_entry()` filters buckets, notifies an observer, hashes the bucket shard to a datalog shard, and chooses between direct push and windowed coalescing. If the watch is unavailable, it pushes directly to the head backend and treats failure as fatal to that call. If the watch is healthy, it marks the shard modified, checks a per-bucket-generation `ChangeStatus`, writes at most once per `rgw_data_log_window`, and registers later changes in a current renewal cycle guarded by semaphores.

`renew_entries()` swaps the current cycle, adds each `BucketGen` key into an in-memory semaphore set, batches encoded `rgw_data_change` records per log shard, pushes them to the head backend, updates expiration timestamps, then decrements the semaphore set on RADOS only after successful backend pushes. This ordering is the core crash-recovery invariant.

Recovery lists semaphore objects, synthesizes data-log entries for outstanding keys, notifies other RGWs to subtract in-flight working sets, then decrements the remaining semaphore counts with a grace period. Watch notifications use `recovery_check` and `recovery_reply` payloads so live RGWs can report keys in `cur_cycle` or local semaphore sets. The watch loop handles overflow, cancellation, unwatch, and rewatch attempts.

Listing flow can list one shard with a string marker or scan all shards with `RGWDataChangesLogMarker`. Generation cursors are prepended to backend-native cursors so callers see one monotonic marker space across backends and log generations.

## State and Persistence Behavior
Persistent state includes generation metadata in `data_loggenerations_metadata`, data-log entries in `data_log.<shard>` or `data_log@G<gen>.<shard>`, and semaphore sets in `_sem_setdata_log.<shard>`. In-memory state includes LRU `changes`, `cur_cycle`, `semaphores`, modified shard notifications, watch cookie, background futures, and cancellation signals. The durable ordering is conservative: semaphores are incremented before deferred changes can be lost, and decremented only after a corresponding log entry is safely pushed or recovered.

## Dependencies and Integration Points
The file integrates with neorados, `cls/log`, `cls/fifo`, `cls/sem_set`, async spawn groups, blocked completion, RGW bucket layout, SAL Rados store, log backing generation helpers, bucket change observers, and admin output. Multisite sync readers depend on `list_entries()` and `get_info()`, while notification senders consume `read_clear_modified()` and v1/v2 notify encoders from the companion notify files.

## Risks and Test Signals
Key risks are duplicate or lost change entries around watch loss, renewal failure, semaphore decrement failure, and generation trimming. `read_sems()` has a subtle error condition that should be tested around ENOENT and end-of-buffer handling. Other risks include invalid `BucketGen` parsing, shard bounds, backend migration, async shutdown races, and FIFO/omap marker compatibility. Test signals should include direct-push fallback, coalesced updates inside and outside the window, crash recovery with outstanding semaphores, notification missed-response handling, generation cursor list/trim behavior, format changes, admin semaphore pagination/reset, and shutdown with background futures present or absent.
