# Research Group: subset-b-008972

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_capacity.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_capacity.c

## Purpose
This file implements WiredTiger's connection-level I/O capacity controller. It parses `io_capacity.total`, derives per-subsystem capacities, starts and stops the capacity server thread, asynchronously flushes accumulated writes, and throttles read, log, checkpoint, and eviction I/O by assigning time reservations proportional to byte counts.

## Important APIs, Types, and Functions
`__wti_capacity_server_create` and `__wti_capacity_server_destroy` are the connection lifecycle entry points. `__capacity_config` validates `io_capacity.total`, sets `WT_THROTTLE.total`, derives `ckpt`, `evict`, `log`, and `read` capacities via `WT_CAPACITY_SYS`, and publishes `capacity_threshold`.

`__capacity_server_start` opens the `capacity-server` internal session, allocates `conn->capacity.cond`, sets `WT_CONN_SERVER_CAPACITY`, and creates the server thread. `__capacity_server` waits on the condition, calls `__wt_fsync_background` after accumulated non-read writes cross the configured threshold, records `fsync_all_time`, and resets `cap->written`.

`__wt_capacity_throttle` is the hot path called by block, block-cache, file-handle, and log write/read code. It maps `WT_THROTTLE_CKPT`, `WT_THROTTLE_EVICT`, `WT_THROTTLE_LOG`, and `WT_THROTTLE_READ` to per-subsystem reservation clocks and statistics. `__capacity_reserve` atomically advances a reservation clock by `WT_RESERVATION_NS(bytes, capacity)`.

## Control Flow and Behavior
Startup first destroys any existing server during reconfigure, then parses capacity settings. In-memory, read-only, and platforms without background fsync skip thread creation even when a total capacity is configured. A nonzero capacity starts a dedicated internal session and condition variable.

The server loop sleeps until signalled, with a periodic one-second wakeup as a missed-signal guard. It exits when `WT_CONN_SERVER_CAPACITY` is cleared. Otherwise it ignores wakeups until `cap->written >= cap->threshold`, performs a background fsync, updates timing stats, and clears the written counter.

Throttle calls return immediately when total capacity is disabled, the selected subsystem has zero capacity, or the connection is recovering. Non-read calls add to `cap->written` and may signal the server. The caller gets a current wall-clock nanosecond timestamp, reserves slots in both the subsystem reservation clock and the total reservation clock, optionally steals unused reservation time from another idle subsystem, then sleeps only when the chosen reservation lies in the future and exceeds `WT_CAPACITY_SLEEP_CUTOFF_US`.

## State and Persistence Behavior
All capacity state is in memory under `conn->capacity.throttle`: configured byte rates, reservation clocks, written byte counters, signal state, and thread/session handles. There is no durable metadata. Reconfiguration resets the server and rewrites the throttle values. The reservation clocks deliberately self-heal if a reservation is more than one second behind wall clock, preventing stale reservation values from causing extreme future or past accounting after idle periods.

Statistics are the observable persistent signal during process lifetime: bytes per subsystem, total bytes written, wait time per subsystem or total cap, `capacity_threshold`, and fsync timing. The background fsync behavior affects durability pressure indirectly but does not create an explicit on-disk record.

## Dependencies and Integration Points
This code integrates with `wiredtiger_open` and reconfigure capacity settings, connection server flags, internal sessions, WT condition variables and thread APIs, atomic operations, connection stats, `__wt_fsync_background`, and I/O call sites such as `block_read.c`, `block_disagg_mgr.c`, `os_fhandle.c`, `block_mgr.c`, and `log.c`.

It relies on capacity constants and macros from WiredTiger internals: `WT_THROTTLE_MIN`, `WT_CAPACITY_SYS`, `WT_CAPACITY_PCT`, `WT_CAPACITY_MIN_THRESHOLD`, `WT_CAPACITY_SLEEP_CUTOFF_US`, `WT_BILLION`, and `WT_STEAL_FRACTION`.

## Risks
The throttle path is lock-free and heavily atomic, so reservation arithmetic must avoid overflow and inconsistent reservation rollback. The code asserts writes are below `16 * WT_GIGABYTE`; larger byte counts could overflow nanosecond calculations. Stealing capacity has a race-sensitive CAS path that subtracts the caller's prior reservation before retrying. Bugs there can undercount or overcount future sleep.

The server's `signalled` flag is not a replacement for the condition variable, so missed or reordered signals are mitigated by the timed wait. Reconfigure destroys and recreates the thread to avoid concurrent config mutation, but callers of `__wt_capacity_throttle` can still observe new `total` values while old reservation clocks remain in memory. Read-only, in-memory, recovery, and unsupported background fsync cases are intentionally no-op paths and should remain so.

## Test Signals
Direct signals are `test_reconfig01.py` for `io_capacity` reconfiguration and minimum validation, `test_txn24.py` for eviction capacity byte stats, and stats counters for `capacity_bytes_*`, `capacity_time_*`, `capacity_threshold`, and `fsync_all_time`. Workloads that configure low capacity should show sleep-time accumulation and lower write throughput; disabled capacity should show no throttling. Recovery tests should verify no capacity sleep during `WT_CONN_RECOVERING`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_capacity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_compact.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_compact.c

## Purpose
This file implements the background compaction server. It tracks per-file compaction outcomes, processes include/exclude eligibility from `WT_SESSION::compact` configuration, walks metadata for `file:` entries, avoids compaction under cache pressure, and runs compaction in a dedicated connection server thread.

## Important APIs, Types, and Functions
`__wti_background_compact_server_create` and `__wti_background_compact_server_destroy` own the server thread, internal session, condition variable, stat hash, and exclude hash. `__wt_background_compact_signal` is the API path that enables or disables background compaction, validates `background`, `run_once`, and `exclude`, prevents reconfiguration while already running, updates `conn->background_compact.config`, and signals the server.

`__background_compact_exclude_list_process`, `__background_compact_exclude_list_add`, `__background_compact_exclude_list_clear`, and `__background_compact_exclude` maintain an exclude hash keyed by table name without the `table:` prefix and checked against `file:` URIs. `__background_compact_get_stat`, `__background_compact_list_insert`, `__background_compact_list_remove`, and `__background_compact_list_cleanup` maintain `WT_BACKGROUND_COMPACT_STAT` entries keyed by file URI and file id.

`__wt_background_compact_start` and `__wt_background_compact_end` are called around actual compact operations to record starting size, ending size, bytes rewritten, success/failure, bytes recovered, and the moving average used by skip heuristics. `__background_compact_find_next_uri` scans the metadata table from the last URI and chooses the next eligible `file:` URI. `__background_compact_server` runs the main loop.

## Control Flow and Behavior
Server creation is skipped for in-memory, read-only, and disaggregated connections. Otherwise the connection allocates per-bucket `stat_hash` and `exclude_list_hash`, opens an internal `compact-server` session with `WT_SESSION_CAN_WAIT | WT_SESSION_IGNORE_CACHE_SIZE`, allocates the condition, and starts the thread.

`__wt_background_compact_signal` serializes commands with `background_compact.lock`. It rejects a new command while a prior signal is pending, rejects background compaction for in-memory/read-only databases, strips `background=` from the config so only real compact options are compared, and refuses config changes while already running. On enable it stores `run_once` and rebuilds the exclude list. It toggles the atomic `running` flag, stores the stripped config, sets `signalled`, and wakes the thread.

The server loop remembers the current metadata URI scan position. When disabled, after a full iteration, or under cache pressure, it waits for the configured full-iteration interval and resets the scan to `file:` when beginning a new pass. While running, it checks dirty and clean eviction pressure before doing work. It then finds the next eligible `file:` metadata entry, copies the latest config under lock, and invokes `WT_SESSION::compact` on that file. `EBUSY`, `ENOENT`, `ETIMEDOUT`, `WT_ROLLBACK`, and interruption `WT_ERROR` from a disabled server are treated as nonfatal background outcomes; other errors panic the connection.

## State and Persistence Behavior
The server's durable inputs are metadata table entries and file sizes. Its own state is in-memory: the scan cursor URI, tracked file stats, skip counts, `bytes_rewritten_ema`, `files_compacted`, `files_skipped`, exclude hash, config string, and `running/run_once/signalled` flags. Tracked stat entries are reset when a file id changes, which handles drop-and-recreate of the same URI. Entries are also removed on disable, exit, or when idle longer than `max_file_idle_time`.

The compaction operation itself rewrites block-manager state and may reclaim file space. This file records the before/after sizes and updates background compaction stats, but compaction persistence is provided by the lower block manager and metadata layers.

## Dependencies and Integration Points
This code depends on metadata cursors, read-uncommitted metadata traversal, `__wt_compact_check_eligibility`, block manager named-size checks, btree file ids, WT compact APIs, connection stats, internal sessions, condition variables, and cache pressure helpers `__wt_evict_dirty_needed`, `__wt_evict_clean_needed`, and `__wt_evict_cache_stuck`.

It integrates with public `WT_SESSION::compact` background mode, `debug_mode=(background_compact)`, format's background compact workload, and csuite tests such as `wt8246_compact_rts_data_correctness`.

## Risks
Metadata traversal is explicitly called out as temporary until a dedicated internal API exists. It uses read-uncommitted scans and loops to avoid returning a key less than or equal to the previous URI; changes here can miss files, loop incorrectly, or compact stale metadata. Exclude entries are specified as `table:` URIs but matched against derived `file:` table names, so naming assumptions matter.

The server avoids cache pressure but compaction can still race with file drops, permission changes, checkpoints, rollback, and application load. The skip heuristic depends on file id, previous success, bytes rewritten EMA, `max_file_skip_time`, and file size; mistakes can cause either too much compaction or starvation. Signal handling must preserve the invariant that a running config cannot be changed in place.

## Test Signals
Useful signals include `background_compact_running`, `background_compact_success`, `background_compact_fail`, `background_compact_timeout`, `background_compact_interrupted`, skip counters for small files, no-such-file, permission, exclude, unsuccessful files, bytes recovered, EMA, and tracked file count. Format workload toggles background compaction, and csuite foreground/background compaction tests check data correctness across rollback-to-stable and compaction. Tests should cover run-once full iteration completion, exclude validation rejecting non-`table:` URIs, disable while compact is active, and drop/recreate id changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_compact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_dhandle.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_dhandle.c

## Purpose
This file manages connection-level data handles. It allocates and hashes handles for btree, layered, table, tiered, and tiered-tree URIs; loads metadata-backed configuration; opens and closes the underlying objects; marks stale handles outdated; applies callbacks across open btrees; discards handles during close; and refreshes write generations after rollback-to-stable.

## Important APIs, Types, and Functions
`__wt_conn_dhandle_alloc` creates a `WT_DATA_HANDLE` or subtype based on URI prefix (`file:`, `layered:`, `table:`, `tier:`, `tiered:`), initializes locks and names, creates a btree payload for btree handles, and inserts it into both the connection list and hash bucket. `__wt_conn_dhandle_find` searches the hash under the handle-list lock and filters dead/outdated handles, with a special exception for in-use read-only btree checkpoints.

`__conn_dhandle_config_set` reads metadata, builds `dhandle->cfg`, strips checkpoint and live-restore fields into `meta_base` for btree/tiered handles, stores hashes and update timestamps, and chooses defaults for layered/table/tier metadata. `__conn_dhandle_config_parse_ts` sets timestamp assertion and write timestamp usage flags.

`__wt_conn_dhandle_open` reopens a handle with fresh metadata, disables eviction for btrees, initializes dsrc stats on demand, opens the underlying object via btree/schema/tiered helpers, records exclusive ownership, sets `WT_DHANDLE_OPEN`, and increments `open_btree_count` for live handles. `__wt_conn_dhandle_close` performs visibility checks, turns eviction exclusive on/off, flushes or discards data, closes the backing object, marks handles dead when requested, and clears open state.

`__wt_conn_dhandle_close_all`, `__wti_conn_dhandle_discard_single`, and `__wti_conn_dhandle_discard` are schema and connection shutdown paths. `__wt_conn_btree_apply` walks one URI bucket or the full connection handle list and applies a callback to open live btree handles. `__wti_conn_dhandle_outdated` marks matching live handles stale. `__wt_dhandle_update_write_gens` updates btree write generations after rollback-to-stable.

## Control Flow and Behavior
Allocation assumes the caller holds the handle-list write lock and double-checks that no matching handle was inserted by another thread. After type-specific allocation, it initializes the btree payload if needed, metadata flag, rwlock, close lock, name/checkpoint copies, then publishes with a release barrier because sweep may scan without the list lock.

Opening requires an exclusive dhandle unless the caller asked for lock-only. If already open, the handle is closed first so special handles such as verify can use fresh flags. Metadata is reloaded and timestamp flags are parsed. The underlying open is type-specific. For btree and tiered handles, special flags are copied to `WT_BTREE`, dsrc stats are allocated lazily, and eviction exclusive mode is cleared before returning. Metadata open failure with `ENOENT` marks the connection corrupt and returns `WT_ERROR`.

Close first verifies there is no uncommitted data when requested, then excludes eviction and sets advisory eviction flags. It avoids acquiring schema locks while holding an exclusive handle by setting `WT_SESSION_NO_SCHEMA_LOCK` if needed. Under `dhandle->close_lock`, it decides whether to discard, checkpoint-close, or mark dead. Memory-mapped btrees are discarded before closing because mapped pages contain pointers into the mapping; non-mapped discard happens after close. If a handle is merely marked dead, sweep closes it later; otherwise open flags and open count are cleared.

Connection shutdown first closes non-metadata and non-history-store handles because closing dirty user files can write metadata and read history store data. It then closes the history store, clears the session cache, blocks new data-handle use on the default session, closes metadata cursors, and discards remaining handles.

## State and Persistence Behavior
The connection maintains `dhqh` and `dhhash`, reference counts, `session_inuse`, exclusive references, open/dead/outdated/dropped flags, btree write generations, metadata config copies, and per-handle locks. Metadata strings are persisted in the metadata table; this file caches them in `dhandle->cfg`, `meta_base`, `orig_meta_base`, hashes, and timestamps to avoid reparsing checkpoint-heavy fields.

Closing may persist a checkpoint through `__wt_checkpoint_close` unless the tree is non-durable, in-memory, no-checkpoint, dead, or being discarded. Marking a handle outdated does not remove persistence; it prevents future cache hits so new opens load newer metadata. `__wt_dhandle_update_write_gens` updates in-memory generation fields so pages read after rollback-to-stable get transaction IDs reset relative to `conn->base_write_gen`.

## Dependencies and Integration Points
This file is central to session dhandle caches, schema operations, sweep, checkpoint, eviction, metadata, tiered storage, layered tables, history store release, rollback-to-stable, and verbose diagnostics. It uses handle-list locks, handle rwlocks, close locks, metadata tracking, meta-track rollback, btree/tiered/schema open and close helpers, checkpoint close, eviction discard, and transaction visibility.

Disaggregated storage uses `__wti_conn_dhandle_outdated` heavily when checkpoint pickup updates local metadata or role transitions make older stable/read-only handles unsafe.

## Risks
Handle publication and removal are concurrency-sensitive. The release barrier before list insertion protects sweep from partially initialized handles. Close ordering must avoid deadlocks between schema locks, handle locks, and history-store dhandle release. Marking a handle dead before closing the block manager can violate block-manager single-reference assumptions, so the code delays that flag.

Visibility checks are required before closing with uncommitted updates; skipping them can drop or checkpoint unresolved data. Conversely, overly strict checks can make schema operations fail with `EBUSY`. Memory-mapped files have special discard ordering. Outdated read-only checkpoint handles remain findable while in use, which is necessary for disaggregated stable checkpoints but can pin older metadata longer.

## Test Signals
Signals include schema drop/rename/truncate behavior under open cursors, checkpoint handle walking stats, sweep cleanup, rollback-to-stable write generation behavior, metadata corruption on missing metadata handle, and disaggregated checkpoint pickup invalidating old handles. `__wti_verbose_dump_handles` gives runtime diagnostics for reference leaks. Tests should stress close-all with live checkpoint handles, dead/outdated filtering, metadata tracking rollback, and close failures from uncommitted data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_dhandle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_handle.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_handle.c

## Purpose
This file performs base initialization and destruction of `WT_CONNECTION_IMPL`. It wires together the connection's global queues, subsystem initialization, spinlocks/rwlocks, statistics, generation manager, block manager queue, and final teardown of connection-owned memory.

## Important APIs, Types, and Functions
`__wti_connection_init` initializes a newly allocated connection using `conn->default_session`. It sets up queue heads for data handles, libraries, data sources, file handles, disaggregated shared metadata operations, and pending crypt keys. It calls subsystem initializers for prefetch, tiered storage, I/O capacity, extensions, configuration, statistics, hot backup, and generations.

The same function initializes core locks: API, checkpoint, background compact, disaggregated shared metadata queue, pending crypt key, file handle list, metadata, reconfigure, schema, turtle file, log debug retention rwlock, dhandle rwlock, table rwlock, and block manager lock. It initializes the block manager queue and clears checkpoint timer stats.

`__wti_connection_destroy` removes the connection from the process global connection queue, discards config and free-on-close memory, destroys locks and subsystems in reverse-ish order, frees hash buckets and recovered checkpoint snapshot memory, releases config/debug/home/session/error-prefix allocations, discards connection stats, and finally frees the connection object.

## Control Flow and Behavior
Initialization is linear and returns on first failure through the `WT_RET`/`WT_DECL_RET` pattern. Queue heads are initialized before subsystems that may append to them. Lock initialization precedes subsystems that need shared synchronization. Capacity init/destroy are currently no-op wrappers but are still called as part of the lifecycle contract.

Destruction first handles a null connection defensively. It removes the connection from `__wt_process.connqh` under the process spinlock, then tears down connection-owned configuration, free-on-close entries, locks, disaggregated pending crypt keys, backup, prefetch, tiered storage, capacity, extensions, hash tables, snapshot memory, strings, session array, and stats. It assumes higher-level close has already stopped server threads and discarded open data handles.

## State and Persistence Behavior
The file initializes in-memory connection state only. Persistent files and metadata are owned by lower subsystems; this code creates the synchronization and collection roots they rely on. Destruction releases memory and locks but does not itself checkpoint or remove persistent data.

## Dependencies and Integration Points
This is a hub for connection lifecycle. It depends on initialization and destroy functions across prefetch, tiered, capacity, extensions, config, stats, backup, generation, and disaggregated subsystems. It also owns lock names used in diagnostics and lock tracking. `conn_dhandle.c`, `conn_compact.c`, `conn_capacity.c`, and disaggregated metadata code all rely on queues and locks initialized here.

## Risks
Ordering is the main risk. Destroying locks before subsystems that still use them can produce shutdown races. Failing midway through initialization leaves some resources initialized and others not; callers must only destroy what was successfully created or tolerate initialized-null patterns. The process connection queue removal must happen exactly once under `__wt_process.spinlock`.

Subsystem additions must update both init and destroy paths. Disaggregated storage adds several queue and lock fields here, so leaks or stale locks can surface during role transitions and shutdown rather than at the point of use.

## Test Signals
The strongest signals are clean connection open/close under sanitizers, repeated open/close with extensions, tiered/disaggregated/background compact/capacity enabled, and failure injection during initialization. Lock leak detectors, process connection queue assertions, and statistics discard checks are useful. Shutdown tests should verify no server thread or dhandle path uses destroyed connection locks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_layered.c

## Purpose
This file owns connection-level disaggregated and layered-table coordination. It configures disaggregated storage, manages leader/follower role transitions, initializes shared metadata, queues metadata operations for checkpoint publication, creates missing stable tables, processes metadata updates into the shared metadata table, handles clean startup-directory behavior for disaggregated mode, and advances global disaggregated checkpoints.

## Important APIs, Types, and Functions
`__wti_disagg_conn_config` parses initial and reconfigure settings for `disaggregated.*`, opens the page log, opens special PALI handles for shared metadata and key provider data, initializes the layered table manager, picks up configured checkpoints, begins or abandons checkpoints for leaders, sets page-delta options, `lose_all_my_data`, and drain thread count, and performs role step-up/step-down on reconfigure.

`__wt_disagg_enqueue_metadata_operation`, `__wti_disagg_shared_metadata_queue_prune`, `__wti_disagg_table_latest_create_remove`, `__wt_disagg_shared_metadata_queue_publish`, `__wt_disagg_shared_metadata_queue_drop_size`, and `__wt_disagg_shared_metadata_queue_process` manage `conn->disaggregated_storage.shared_metadata_qh`. Queue entries capture stable, table, colgroup, and layered metadata values, a schema epoch, a metadata operation (`CREATE`, `UPDATE`, `REMOVE`), and a deferred bit.

`__layered_create_missing_stable_tables` and helpers create stable constituents from layered metadata after follower step-up. The schema-epoch path replays queued create entries newer than the last stable checkpoint while skipping creates followed by removes. The legacy path scans local metadata for `layered:` entries and creates missing stable tables best-effort.

`__disagg_step_up`, `__disagg_step_down`, `__disagg_abandon_checkpoint`, `__disagg_begin_checkpoint`, and `__disagg_restart_checkpoint` implement role transitions and checkpoint state. `__wt_disagg_advance_checkpoint` completes a global checkpoint through the page log and starts the next one. `__wti_ensure_clean_startup_dir` removes or rejects stale local WiredTiger files for disaggregated "lose all my data" startup.

## Control Flow and Behavior
On initial config, the connection records the configured role, opens the page log, opens PALI handles for the shared metadata table and key-provider table, and, if disaggregated mode is active, rejects read-only mode, initializes the layered table manager, optionally abandons incomplete checkpoints as leader, creates the shared metadata table, picks up a supplied checkpoint, or as a startup leader attempts to find and pick up the latest complete checkpoint before beginning a new checkpoint.

On reconfigure, a follower may pick up `disaggregated.checkpoint_meta`. Role changes happen under the checkpoint lock. Step-up sets the leader flag first, abandons any incomplete checkpoint, begins a new checkpoint, creates missing stable tables, drains ingest tables into stable tables, and marks the shared disk cache read-only with a timestamp. Step-down marks open disaggregated btrees read-only and outdated under the handle-list read lock before clearing leader state, clears the metadata queue, and reactivates or initializes the shared disk cache for follower use.

Metadata operations are enqueued while the schema lock is held. Schema operations start deferred so operations already present at checkpoint start are processed at checkpoint end, while concurrent operations wait for a later checkpoint. Queue processing holds the schema lock and queue lock, skips deferred or future-epoch entries, handles create/remove pairs for tables that never had stable metadata, applies operations to the shared metadata table, and frees processed entries. It panics on API violations where a published create needs shared metadata but the stable table was never created before a later drop.

Checkpoint advance is leader-only. On success it formats checkpoint metadata containing metadata LSN, checksum, database size, version, and compatible version, calls `pl_complete_checkpoint`, stores the checkpoint timestamp, logs completion, and begins the next checkpoint. On unsuccessful checkpoint it skips completion but still begins the next checkpoint.

## State and Persistence Behavior
Persistent state includes the disaggregated shared metadata table, PALI page-log checkpoint completion records, stable table metadata copied to shared storage, local metadata updated by checkpoint pickup, and the local filesystem cleanup behavior in disaggregated mode. In-memory state includes role, page-log handles, metadata queue entries, last materialized LSN, last checkpoint metadata LSN/checksum/root/timestamps, database size, page-delta config, shared disk cache state, and drain thread count.

Schema epochs are the consistency boundary for metadata publication. `WT_SCHEMA_EPOCH_UNPUBLISHED` entries are published later by `__wt_disagg_shared_metadata_queue_publish`; queue pruning removes entries at or below a completed checkpoint's schema epoch. The leader's checkpoint lock serializes role transitions, checkpoint begin/complete, and checkpoint abandonment.

## Dependencies and Integration Points
This file integrates with schema creation, metadata cursors, the layered table manager, ingest-table drain code in `conn_layered_ingest.c`, checkpoint pickup in `conn_layered_checkpoint_pick_up.c`, page-log helpers in `conn_layered_page_log.c`, key provider loading, shared disk cache, block-disaggregated metadata, checkpoint, transaction-global timestamps, and connection reconfiguration.

It is also called by schema paths that enqueue shared metadata operations, checkpoint paths that process/drop-size/prune the queue, startup code that cleans directories, and role-management tests that reconfigure `disaggregated.role`.

## Risks
Role transition ordering is high risk. Step-up sets leader mode before abandoning/restarting checkpoints and draining ingest tables because later operations depend on leader behavior. If the checkpoint lock is not held, a checkpoint can observe half of a role transition. Step-down must make btrees read-only before clearing leader state to prevent eviction or split paths from dirtying pages in the follower window.

Shared metadata queue ordering and schema epoch validation are critical. A create followed by remove can be safely skipped only when no checkpoint needed the table in between. Update operations must not publish stable data before the table create is visible. Missing stable values, future epochs, or out-of-order epochs can cause followers to miss metadata or require a panic to avoid silent inconsistency.

Startup cleanup can delete local WiredTiger files when `lose_all_my_data` and local file action permit it. The filter must keep lock and stat files as intended while removing files that would make disaggregated startup read stale local state.

## Test Signals
Relevant tests include `test_layered_stepup01.py`, `test_layered_stepup02.py`, layered follower/cursor/fast-truncate/prepare suites, disaggregated model and cppsuite failover tests, and format disaggregated configurations with `disagg.drain_threads` and `preserve_prepared`. Stats include role, step-up/down time, checkpoint metadata apply/defer counts, database size, checkpoint completion, and abandon checkpoint success/failure. Failure-injection signals include `WT_TIMING_STRESS_FAILPOINT_DISAGG_CHECKPOINT_QUEUE_DRAIN` and panic paths for bad queue ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered_checkpoint_pick_up.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_layered_checkpoint_pick_up.c

## Purpose
This file implements follower checkpoint pickup for disaggregated storage. It parses checkpoint metadata supplied through configuration, fetches shared metadata from the page log, updates the local metadata table with the picked-up shared metadata checkpoint, reconciles local and shared table/file metadata, creates missing ingest tables, invalidates stale handles, updates checkpoint bookkeeping, and validates checkpoint metadata versions.

## Important APIs, Types, and Functions
`__wti_disagg_pick_up_checkpoint_meta` is the external entry point. It copies the metadata config string, parses `metadata_lsn`, optional `metadata_checksum`, `database_size`, `version`, and `compatible_version`, opens an internal `checkpoint-pick-up` session, and calls `__disagg_pick_up_checkpoint` under the checkpoint lock.

`__disagg_pick_up_checkpoint` rejects older metadata LSNs, warns and exits for duplicate LSNs, fetches the shared metadata page with `__wti_disagg_fetch_shared_meta`, parses it with `__wt_disagg_parse_meta`, loads crypt key metadata if configured, updates the local metadata entry for `WT_DISAGG_METADATA_URI`, applies per-table metadata through `__disagg_apply_checkpoint_meta`, prunes the local shared-metadata operation queue, finalizes checkpoint state, and updates success/failure stats.

`__disagg_apply_checkpoint_meta` is the main reconciliation loop. It opens local metadata cursors and checkpoint cursors on the shared metadata table for `colgroup:`, `file:`, `layered:`, and `table:` prefixes. It advances all cursors in sorted logical table-name order, compares local/shared presence for each URI scheme, inserts new metadata, updates existing file checkpoint metadata, creates missing ingest tables from layered config, and handles local-only or dropped-table cases.

Helper functions include `__disagg_save_checkpoint_meta_local`, `__disagg_update_file_meta`, `__disagg_insert_meta`, `__disagg_bound_cursor`, `__disagg_table_name`, `__disagg_file_skip_local`, `__disagg_discard_old_checkpoint_check`, `__layered_create_missing_ingest_table`, `__raise_next_file_id`, and `__disagg_finalize_checkpoint_meta`.

## Control Flow and Behavior
The pickup entry point first turns a bounded config slice into a null-terminated string. It treats missing checksum as a backward-compatible warning, validates metadata version compatibility, then uses an internal session and checkpoint lock so pickup cannot race checkpoint begin/advance or role transition.

Pickup first checks LSN monotonicity against `last_checkpoint_meta_lsn`. It then fetches and parses the shared metadata root. The local shared metadata table entry is updated by collapsing the new `checkpoint=` config into its local metadata record. If the checkpoint changed, any old checkpoint handle for the shared metadata table is marked outdated.

The metadata apply loop opens four local and four shared cursors, bounds each by URI scheme, and processes all metadata for one logical table name at a time. Existing layered tables get their stable `file:` checkpoint metadata updated or inserted. New layered tables are ignored if the local metadata queue says the latest local create/remove operation is `REMOVE`; otherwise the code creates the ingest table if referenced and absent, then inserts layered, file, colgroup, and table entries from shared metadata. Non-layered shared table, colgroup, and file entries are inserted or updated where supported. Local metadata entries without shared counterparts are currently logged but mostly left in place.

Finalization stores the new checkpoint metadata LSN, schema epoch, checkpoint timestamp, oldest timestamp, transaction-global checkpoint timestamp fields, database size, last checkpoint root string, updates ingest prune timestamps, and raises `next_file_id` if needed.

## State and Persistence Behavior
The persistent effects are local metadata table updates and optional creation of missing ingest tables. Local metadata's `checkpoint=` fields for stable/shared files are overwritten with checkpoint information from the shared metadata checkpoint, while other metadata fields are preserved through config collapse. Old checkpoint dhandles are marked outdated so future opens use the new metadata.

In-memory state updated during finalization includes checkpoint metadata LSN, schema epoch, checkpoint timestamps, database size, last checkpoint root, transaction-global last checkpoint timestamp, and file id allocator. The code also prunes the connection's pending shared metadata queue up to the picked-up schema epoch, because those operations are now represented in shared metadata.

## Dependencies and Integration Points
This file depends on PALI/page-log metadata fetch and parse helpers, local and shared metadata cursors, layered table schema config, dhandle invalidation, schema locks, checkpoint locks, key provider loading, ingest prune logic from `conn_layered_ingest.c`, and shared metadata queue inspection from `conn_layered.c`.

It integrates with `__wti_disagg_conn_config` during startup and follower reconfigure, model/cppsuite helpers that call `reconfigure(disaggregated=(checkpoint_meta=...))`, and tests for layered follower pickup and failover.

## Risks
The four-way cursor merge is correctness-critical. Table names are derived differently for `file:` keys by stripping `.wt` and `.wt_stable`, and local ingest files are skipped so they are not mistaken for shared stable files. Bugs in name normalization or cursor advancement can pair metadata entries from different tables or miss a URI scheme.

The code updates only checkpoint information for existing file metadata and has FIXME notes about verifying all other metadata fields. If leader and follower metadata diverge outside checkpoint config, pickup may not detect it. Dropped local layered tables are not fully removed yet. Creating missing ingest tables from shared layered config depends on key/value format extraction and schema create under the schema lock.

Older checkpoint pickup is rejected, duplicate pickup is a no-op, and incompatible metadata versions return `ENOTSUP`. These guards protect followers from rolling back state or reading a newer checkpoint format incorrectly.

## Test Signals
Signals include `layered_table_manager_checkpoints_disagg_pick_up_succeed`, follower pickup count, failure count, `disagg_apply_checkpoint_meta_time`, inserted/updated file metadata stats, updated database size, last checkpoint timestamps, and stale dhandle invalidation. Tests should cover new layered table pickup, existing table checkpoint update, shared history store file-only entries, dropped table races, duplicate and older metadata LSN handling, missing checksum backward compatibility, incompatible version rejection, and missing shared file metadata errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered_checkpoint_pick_up.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered_ingest.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_layered_ingest.c

## Purpose
This file drains disaggregated layered ingest tables into stable tables, replays follower-recorded truncates in timestamp order, handles prepared-update edge cases during step-up, clears ingest tables after drain, and advances ingest-table prune timestamps for garbage collection after checkpoints.

## Important APIs, Types, and Functions
`__wti_layered_drain_ingest_tables` is the step-up entry point. It initializes `conn->layered_drain_data.work_queue`, starts optional drain worker threads, queues open ingest dhandles, uses the caller thread as a worker, stops the thread group, and clears remaining work.

`__layered_copy_ingest_table` is the core data movement routine. It derives the stable URI from an ingest URI, opens the stable table with overwrite, opens a version cursor on the ingest table with raw key/value and timestamp-order dump options, builds update chains for each key whose durable timestamp falls in a requested range, fixes or resolves prepared transactions when needed, and applies updates to stable via `__layered_move_updates`.

`__layered_drain_ingest_table_and_truncate_list` derives the parent layered URI, obtains committed truncates from `WT_LAYERED_TABLE.truncateqh`, sorts them by start timestamp with `__truncate_cmp_by_start_ts`, copies ingest updates between truncate timestamps, replays each truncate with `__layered_apply_truncate_to_stable`, and then copies the remaining updates through `WT_TS_MAX`.

Prepared-update helpers include `__layered_assert_stable_btree_state`, `__layered_fix_prepared_transaction_callback`, and `__layered_fix_prepared_transaction`. GC helpers include `__layered_update_ingest_table_prune_timestamp`, `__wti_layered_iterate_ingest_tables_for_gc_pruning`, and `__layered_last_checkpoint_order`.

## Control Flow and Behavior
Step-up drain scans the connection's open dhandle list under the handle-list read lock and queues open btree handles whose URI is an ingest table. Each queued dhandle is pinned via `session_inuse`; the worker decrements that pin when done. If `drain_threads > 1`, a thread group runs workers in parallel while the initiating thread also drains work items until the queue is empty.

For each ingest table, the worker copies ingest data to the stable table interleaved with committed truncates, truncates the ingest table in its own timestamp-free transaction, optionally verifies it is empty in diagnostic builds, and resets its prune timestamp to `WT_TS_NONE` so dirty ingest pages can be evicted immediately after step-up.

The copy routine uses a version cursor that can skip updates at or below the later of `from_ts` and the last checkpoint timestamp. Prepared updates are included only on the final pass to `WT_TS_MAX`. For each key, it accumulates a linked list of `WT_UPDATE` objects representing standard values, tombstones, unresolved prepared updates, resolved prepared updates, or aborted prepared updates. Before applying the chain, it searches the stable btree and asserts stable-side invariants: no unresolved preserved prepared update remains unless it is being resolved, and tombstones have a value to delete unless globally visible.

When preserve-prepared is enabled, the code either resolves previously checkpointed prepared cells on stable or patches in-flight prepared transaction operations so later commit/rollback refers to the stable btree instead of the ingest btree. Follower-recorded fast truncates are replayed against stable with `WT_SESSION_INGEST_REPLAY` and the original transaction id, commit timestamp, and durable timestamp.

After checkpoints, pruning walks the layered table manager entries. For each layered table it computes which stable checkpoints are still in use by checkpoint dhandles, derives a safe prune timestamp, opens the ingest btree if available, and monotonically advances `btree->prune_timestamp`.

## State and Persistence Behavior
Draining persists ingest updates into stable tables by modifying stable btrees. It then clears ingest contents with truncate. The operation is part of role transition rather than a user transaction stream; it assumes no competing transactions except the prepared transaction repair cases explicitly handled.

The work queue and thread state are in-memory and destroyed after drain. Truncate entries live on the layered table and are cleared after replay. Prepared transaction repair mutates in-memory transaction operation arrays and dhandle `session_inuse` counts so later transaction resolution remains balanced. Prune timestamps are in-memory btree fields used by eviction/GC to decide which ingest content can be removed.

## Dependencies and Integration Points
This file integrates with layered cursor/truncate code, transaction prepared-state machinery, version cursors, btree row search/modify, schema open/truncate APIs, dhandle reference accounting, layered table manager entries, checkpoint metadata, and disaggregated role step-up in `conn_layered.c`.

It is closely tied to `WT_CONN_PRESERVE_PREPARED`, timestamp rules, disaggregated stable/ingest URI naming (`.wt_stable`, `.wt_ingest`), and checkpoint pickup finalization, which calls `__wti_layered_iterate_ingest_tables_for_gc_pruning`.

## Risks
This is a high-risk data movement path. Timestamp range partitioning must be correct so updates before each truncate are copied before replaying that truncate and later updates are copied afterward. Prepared transaction handling is explicitly temporary and assumes no concurrent commit/rollback and no prepared fast-truncate operations.

The stable btree assertions protect against illegal delta chains, unresolved prepared cells, and tombstones without values. If step-down/step-up carries stale btree pages across roles, drain can encounter prepared state that reconciliation cannot represent. Worker parallelism depends on pinning dhandles correctly and clearing the queue on errors without leaks.

Prune timestamp computation depends on checkpoint handle naming and reference counts. If it advances too far, needed ingest history can be pruned while a checkpoint cursor still needs it; if it does not advance, ingest garbage accumulates.

## Test Signals
Signals include layered step-up tests, layered prepare tests, layered fast-truncate tests, disaggregated format configurations with variable `disagg.drain_threads`, and model failover tests that pick up checkpoints then reconfigure to leader. Diagnostic assertions check empty ingest tables and stable btree prepared/tombstone invariants. Useful runtime checks are successful step-up, no leaked dhandle references, stable table contents matching ingest history plus truncates, correct commit/rollback of prepared transactions after drain, and monotonic ingest prune timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered_ingest.c -->
