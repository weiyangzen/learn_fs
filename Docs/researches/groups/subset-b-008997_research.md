# subset-b-008997 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/thread_group.c -->
# sources/storage-engines/wiredtiger/src/support/thread_group.c Research

## Purpose
This file implements WiredTiger's generic utility-thread group abstraction. A `WT_THREAD_GROUP` owns an array of `WT_THREAD` slots, a group rwlock, a condition used by waiters, and callback pointers supplied by the subsystem. The implementation separates thread existence from active work: resize creates or destroys thread/session/condition resources, while start and stop only toggle `WT_THREAD_ACTIVE` within the already allocated group.

## Important APIs, Types, and Functions
- `WT_THREAD_GROUP` stores `min`, `max`, `alloc`, `current_threads`, `threads`, `lock`, `wait_cond`, name, and callback pointers.
- `WT_THREAD` stores an internal session, thread id/name index, pause condition, run/check/stop callbacks, and flags such as `WT_THREAD_RUN`, `WT_THREAD_ACTIVE`, and `WT_THREAD_PANIC_FAIL`.
- `__thread_run` is the wrapper loop for every worker. It waits while inactive, clears per-thread error log state, calls the configured run callback, invokes an optional stop callback, and panics the connection for unrecoverable utility-thread failures when requested.
- `__thread_group_resize` and public `__wt_thread_group_resize` enforce `min <= max`, shrink before growth, grow the pointer array when needed, open one internal session per new thread, allocate the thread condition, create OS threads inactive, and activate up to `new_min`.
- `__thread_group_shrink` clears active/run flags above the new count, signals their conditions, joins threads without holding the group lock, closes sessions, destroys conditions, and frees slots.
- `__wt_thread_group_create`, `__wt_thread_group_destroy`, `__wt_thread_group_start_one`, `__wt_thread_group_stop_one`, and `__wt_thread_group_foreach` expose lifecycle, active-count control, and per-thread callbacks.

## Control Flow and State
Creation initializes lock and wait condition, records callbacks/name, then delegates to resize under the write lock. Resize first shrinks down to the new maximum so excess OS threads are stopped before allocation metadata changes. New slots are initialized from the old maximum to the new maximum and are launched with `WT_THREAD_RUN` set but without `WT_THREAD_ACTIVE`; the wrapper will sleep on `pause_cond` until activated. `current_threads` is an atomic count of active slots and doubles as the next start/stop index. Start increments it with `__wt_atomic_fetch_add_uint32`, marks that slot active, and signals the thread. Stop decrements it with `__wt_atomic_sub_uint32`, clears active, and signals the pause condition so the worker can re-check state.

## State and Persistence Behavior
This module is entirely in-memory. Persistence is indirect: utility threads may belong to subsystems such as eviction, checkpointing, or tiered storage that perform persistent work. The module's durable correctness role is ensuring those subsystem threads start, pause, shut down, and clean up consistently. Each thread has a dedicated internal session, so session lifecycle must match thread lifecycle exactly.

## Dependencies and Integration Points
The code depends on WiredTiger internal synchronization, atomics, condition variables, session management, verbose logging, and panic/error helpers. Subsystems integrate by supplying `chk_func`, `run_func`, and `stop_func`. `WT_THREAD_CAN_WAIT` controls whether internal sessions are opened with `WT_SESSION_CAN_WAIT`; `WT_THREAD_PANIC_FAIL` escalates callback failure to a connection panic.

## Risks and Edge Cases
Resizing is sensitive because it joins without the lock to avoid deadlock with threads that may need the group lock. Start/stop index arithmetic depends on `current_threads` and the invariant that active threads occupy the low slots. Error handling during resize is intentionally fatal: partial allocation failure destroys the group and panics, because a half-resized utility group can leave important background services inconsistent. `foreach` documents undefined behavior if called while threads are doing work and has a TODO to enforce this.

## Test Signals
Useful coverage includes create/destroy at min/max boundaries, resize growth and shrink with active workers sleeping on long condition waits, callback failure with and without panic flag, repeated start/stop respecting min/max, and sanitizer runs around lock handoff in shrink. Integration tests should watch for leaked internal sessions, stuck joins, missed condition signals, and active-count statistics during subsystem shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/thread_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/timestamp.c -->
# sources/storage-engines/wiredtiger/src/support/timestamp.c Research

## Purpose
This support file centralizes timestamp and time-window string formatting plus validation of WiredTiger time metadata. It validates both per-value `WT_TIME_WINDOW` instances and page-level `WT_TIME_AGGREGATE` summaries, including their relationship to parent aggregates and the stable timestamp when parent aggregate information is absent.

## Important APIs, Types, and Functions
- `__wt_timestamp_to_string`, `__wt_time_point_to_string`, `__wt_time_window_to_string`, and `__wt_time_aggregate_to_string` format timestamp structures for diagnostics and error messages.
- `__wt_timestamp_to_hex_string` emits compact hexadecimal metadata form, with special handling for `WT_TS_NONE` and `WT_TS_MAX`.
- `__wt_verbose_timestamp` logs timestamp values under the timestamp verbose category.
- `__wt_time_aggregate_validate` checks page aggregate invariants and optionally checks containment within a parent aggregate.
- `__wt_time_value_validate` checks individual value time windows and optionally validates them against a parent aggregate.
- Static helpers `__time_aggregate_validate_parent_stable`, `__time_aggregate_validate_parent`, `__time_value_validate_parent_stable`, and `__time_value_validate_parent` implement the two parent modes.

## Control Flow and State
The formatting functions are leaf helpers: they write caller-owned buffers using WiredTiger snprintf utilities. Validation functions first enforce intrinsic ordering constraints, then decide whether parent validation is required. Metadata handles skip parent checks. If `parent == NULL` or the handle is metadata, validation succeeds after local checks. If a parent aggregate is empty, the child is checked against `__wt_get_stable_timestamp(session)` because an empty parent usually means there is no reliable aggregate data from older versions or downgrades. Otherwise the child time points must be contained by parent bounds.

## State and Persistence Behavior
The file does not mutate durable state. Its persistence impact is defensive: time windows and aggregates are embedded in pages, cells, history-store records, and metadata, and bad ordering can corrupt visibility or checkpoint behavior. It explicitly allows cases needed for timestampless truncates and upgrade/downgrade history, such as stop timestamps of `WT_TS_NONE` and empty parent aggregates treated as stable.

## Dependencies and Integration Points
The code depends on `WT_TIME_WINDOW`, `WT_TIME_AGGREGATE`, timestamp constants, transaction id constants, prepare flags, connection flag `WT_CONN_PRESERVE_PREPARED`, `WT_IS_METADATA`, and stable timestamp access. It is used by reconciliation, page validation, diagnostics, transaction/timestamp code, and tiered metadata formatting via `__wt_timestamp_to_hex_string`.

## Risks and Edge Cases
Validation is deliberately nuanced. A too-strict check can reject valid timestampless truncate or downgrade data; a too-loose check can permit impossible visibility intervals. Prepared updates are special: prepared start/stop windows must have prepare timestamps, and when preserve-prepared is active they must also have prepared ids; prepared windows must not simultaneously expose normal start/stop durable timestamps. Parent-empty checks use the current stable timestamp, so failures can be timing-sensitive. Error text depends on stack buffers, so callers must pass buffers sized by WiredTiger constants.

## Test Signals
Test cases should cover normal insert-only, all-deleted, and partially-deleted aggregate scenarios described in comments; timestampless truncate paths; parent containment failures; empty-parent stable timestamp failures; start/stop prepared windows with preserve-prepared both enabled and disabled; and metadata handles skipping parent checks. Negative tests should assert the exact class of `EINVAL` while silent mode returns `EINVAL` without emitting the formatted message.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/update_vector.c -->
# sources/storage-engines/wiredtiger/src/support/update_vector.c Research

## Purpose
This file implements `WT_UPDATE_VECTOR`, a small stack-first vector of `WT_UPDATE *` pointers. It is optimized for the common case where only a small number of updates are collected, avoiding heap allocation until the embedded stack buffer is exhausted.

## Important APIs, Types, and Functions
- `__wt_update_vector_init` zeroes the structure, records the owning session, and points `listp` at the embedded `list` array.
- `__wt_update_vector_push` appends one update pointer, migrating from stack storage to heap storage via `__wt_realloc_def` when `size >= WT_UPDATE_VECTOR_STACK_SIZE`.
- `__wt_update_vector_pop` and `__wt_update_vector_peek` return the last update pointer and assert the vector is non-empty.
- `__wt_update_vector_clear` resets logical size without freeing heap storage.
- `__wt_update_vector_free` frees heap storage if it exists and reinitializes the vector.

## Control Flow and State
The vector starts with `allocated_bytes == 0` and `listp == list`. On the first push beyond stack capacity, it temporarily sets `listp = NULL`, reallocates enough heap capacity for `size + 1`, and copies the embedded stack array to the heap. Later growth uses realloc in place. If migration allocation fails, the error path restores `listp` to the stack buffer and clears `allocated_bytes`, preserving the pre-call vector contents.

## State and Persistence Behavior
The vector owns only pointer-array storage, not the pointed-to `WT_UPDATE` objects. Clearing or freeing the vector does not free updates. Persistence behavior is indirect: callers use the collected update pointers during transaction, reconciliation, or visibility algorithms, and this helper's job is to preserve collection order and memory safety.

## Dependencies and Integration Points
The file depends on WiredTiger allocation helpers, assertion macros, `WT_UPDATE`, and `WT_UPDATE_VECTOR_STACK_SIZE`. It is a reusable support container and has no direct storage-engine policy.

## Risks and Edge Cases
The critical edge case is migration failure from stack to heap; the code explicitly restores the original stack-backed state. Pop and peek are assertion-protected rather than error-returning, so callers must guarantee non-empty state. Because `clear` keeps heap memory, long-lived vectors that temporarily grow large retain that allocation until `free` is called. The vector is not synchronized and must remain session-local or externally protected.

## Test Signals
Unit tests should push exactly stack capacity, stack capacity plus one, and many more elements; verify order through peek/pop; inject allocation failure during first heap migration; verify `clear` preserves reusable heap capacity; and verify `free` returns the vector to stack-backed initialized state.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/support/update_vector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/tiered/tiered_config.c -->
# sources/storage-engines/wiredtiger/src/tiered/tiered_config.c Research

## Purpose
This file parses and applies tiered-storage bucket configuration at connection and table scope. It builds or reuses `WT_BUCKET_STORAGE` instances, customizes storage-source file systems, enforces compatibility rules, and stores connection-level tiered options such as interval and local retention.

## Important APIs, Types, and Functions
- `__tiered_common_config` reads common options such as `tiered_storage.local_retention` into `WT_BUCKET_STORAGE::retain_secs`.
- `__wti_tiered_bucket_config` resolves `tiered_storage.name`, opens a named storage source, validates bucket and prefix requirements, reuses existing bucket storage by hash lookup, or creates and registers a new `WT_BUCKET_STORAGE`.
- `__wt_tiered_conn_config` configures `conn->bstorage`, rejects incompatible connection modes, sets `conn->tiered.interval`, updates tiered statistics, and initializes the special `bstorage_none` file-system mapping.

## Control Flow and State
Bucket configuration starts by opening the named storage source under `conn->ext.storage_lock`. If no storage source is named, the function rejects stray bucket settings and returns no bucket storage. If table-level tiering is requested without connection tiering, it returns `EINVAL`. A table cannot enable shared tiering unless the connection bucket storage is also shared. Existing bucket storage is found by hashing the bucket name and matching bucket plus prefix. New bucket storage duplicates auth token, bucket, prefix, cache directory, calls `ss_customize_file_system`, inserts into source queues and hash queues, marks it freeable, and applies common retention settings.

## State and Persistence Behavior
This module mutates connection in-memory state and extension-owned storage-source queues. It does not itself write metadata, but its result is embedded into tiered handles that later create object metadata and schedule flush/remove work. Retention seconds directly influence when local objects are removed after shared flush.

## Dependencies and Integration Points
The code integrates with the extension storage-source registry, named storage source lookup, CityHash bucket hashing, WiredTiger config parsing, connection flags, statistics, and tiered handle open paths. `__wti_tiered_bucket_config` is used by both connection configuration and per-table tiered open logic.

## Risks and Edge Cases
The function holds `storage_lock` while opening/customizing storage sources and manipulating queue/hash membership, so any storage-source callback that calls back into locked extension state could deadlock if contracts are violated. The error path frees only selected fields of `new`; auth/cache/file-system cleanup depends on storage-source ownership conventions and broader close cleanup. Reconfiguration only reapplies common options to existing connection storage and intentionally does not remove newly created bucket storage if a later connection config step fails.

## Test Signals
Tests should validate missing name plus bucket rejection, missing bucket/prefix rejection, table tiering without connection tiering rejection, shared mismatch rejection, reuse of identical bucket/prefix storage, distinct prefix producing distinct storage, retention reconfiguration, in-memory connection incompatibility, and storage-source customize failures restoring `conn->bstorage` in `__wt_tiered_conn_config`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/tiered/tiered_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/tiered/tiered_handle.c -->
# sources/storage-engines/wiredtiger/src/tiered/tiered_handle.c Research

## Purpose
This file owns tiered table handle lifecycle and object switching. It creates and opens tiered data handles, generates local/shared/object names, manages tier arrays and dhandle references, writes tiered metadata, detects stale shared objects on create, and schedules tiered work when switching objects or restarting after a crash.

## Important APIs, Types, and Functions
- Name and existence helpers: `__tiered_name_check`, `__tiered_name_str`, and public `__wt_tiered_name`.
- Dhandle setup helpers: `__tiered_dhandle_setup`, `__tiered_init_tiers`, `__tiered_update_dhandles`, and `__tiered_cleanup_tiers`.
- Object and metadata creation: `__tiered_create_local`, `__tiered_create_object`, `__tiered_create_tier_tree`, `__wt_tiered_set_metadata`, and `__tiered_update_metadata`.
- Switching and restart: `__tiered_restart_work`, internal `__tiered_switch`, and public `__wt_tiered_switch`.
- Lifecycle APIs: `__wt_tiered_open`, `__wt_tiered_close`, `__wt_tiered_discard`, `__wt_tiered_tree_open`, and `__wt_tiered_tree_close`.

## Control Flow and State
Open starts by resolving bucket storage from table or connection config, merging config for later metadata updates, and constructing object config with `readonly=true,tiered_object=true`. It reads key/value formats, `last`, `oldest`, and `tiers`. Existing tiered handles initialize dhandles from the tiers list and may switch during import. New handles first check shared storage for old objects with the same logical table name, then switch to create initial local metadata.

Switching runs under metadata tracking and is documented as single-threaded. It decides whether an `object:` metadata entry and `tier:` shared tree are needed from the existing local/shared tier state. It optionally requeues restart work for unflushed earlier objects on first flush after restart. It creates object metadata for the current local object, queues a flush work unit, creates the next local `file:` object, updates the `tiered:` metadata with `flush_time`, `flush_timestamp`, `last`, `oldest`, and `tiers`, commits metadata tracking, then refreshes dhandle references.

## State and Persistence Behavior
This is a persistent metadata module. It creates and updates `tiered:`, `file:`, `object:`, and `tier:` metadata entries and uses metadata tracking so multi-step switch operations commit or roll back together. It stores object ids in `current_id`, `next_id`, and `oldest_id`, and records tier names plus operation flags in the tier array. It also writes flush metadata from the active btree's `flush_most_recent_secs` and `flush_most_recent_ts`.

## Dependencies and Integration Points
The file depends on schema create/update, metadata cursor/search/insert, import metadata, btree open/close/discard, dhandle acquisition/release, tiered work queue functions, storage-source file-system directory listing, timestamp hex formatting, and config merge/collapse utilities. It bridges connection/table configuration from `tiered_config.c` with asynchronous work in `tiered_work.c`.

## Risks and Edge Cases
Object switching is complex and must remain single-threaded. A crash between metadata steps is handled by metadata tracking and restart work scanning, but ordering bugs can leave local objects unflushed or dhandles stale. `__tiered_name_check` uses prefix and fixed-length object naming to avoid false positives from superset names; changes to name format must preserve that assumption. Dhandle reference counts are manually incremented/decremented, so missed cleanup risks handle leaks or premature sweep. Import paths insert metadata for objects that may or may not exist and tolerate missing old objects. The code still has temporary `#if 1` dead code to satisfy style checks, suggesting some shared-remove paths are not fully wired.

## Test Signals
Tests should cover creating a new tiered table, reopening existing local/shared states for all documented `tiers` combinations, object switch metadata atomicity, import switching, stale shared-object create rejection, crash/restart with unflushed local objects, dhandle reference cleanup on open failure, correct name generation for local/object/shared/prefix/name-only modes, and retention/flush work queue scheduling after switch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/tiered/tiered_handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/tiered/tiered_work.c -->
# sources/storage-engines/wiredtiger/src/tiered/tiered_work.c Research

## Purpose
This file implements the in-memory tiered-storage work queue. It creates, enqueues, dequeues, requeues, waits for, and frees `WT_TIERED_WORK_UNIT` entries for flush, flush-finish, local-remove, and shared-remove actions.

## Important APIs, Types, and Functions
- `__wt_tiered_work_free` releases the referenced tiered dhandle, updates flush-state accounting, signals flush waiters when all flush work is done, and frees the entry.
- `__wt_tiered_remove_work` removes all queued work for a tiered handle.
- `__wt_tiered_requeue_work` pushes an existing work item back without taking a new dhandle reference.
- Getter APIs `__wt_tiered_get_flush_finish`, `__wt_tiered_get_flush`, `__wt_tiered_get_remove_local`, and `__wti_tiered_get_remove_shared` pop matching work.
- Put APIs `__wt_tiered_put_flush_finish`, `__wt_tiered_put_remove_local`, `__wti_tiered_put_remove_shared`, and `__wti_tiered_put_flush` allocate and enqueue new work.
- `__wt_tiered_flush_work_wait` polls for queued flush work up to a caller-provided timeout.

## Control Flow and State
New work is allocated by a put function, initialized with type, object id, tiered pointer, and optional `op_val`, then passed to `__tiered_push_new_work`, which increments the tiered data-handle in-use count. Internal push takes `conn->tiered.tiered_lock`, appends to `conn->tiered.tieredqh`, increments creation statistics, releases the lock, adjusts atomic `flush_state` for flush work, and signals the tiered worker condition. Pop first does an unsafe empty peek to avoid unnecessary locking, then scans the queue under lock for a matching type and optional maximum `op_val`.

## State and Persistence Behavior
The queue itself is in-memory and not durable. Durability recovery is handled by `tiered_handle.c`, which scans metadata/local files and requeues needed work after restart. `op_val` is used either as a checkpoint generation bound for flush or as an expiration time for local-remove work. Dhandle acquisition keeps tiered handles from being swept while queued work references them.

## Dependencies and Integration Points
The queue depends on connection tiered state, spin locks, condition variables, queue macros, dhandle reference macros, atomic flush-state counters, statistics, and retention settings in `WT_BUCKET_STORAGE`. Tiered worker threads consume entries through the getter functions and must free or requeue entries.

## Risks and Edge Cases
Flush-state accounting must stay balanced across enqueue, requeue, and free; double-free or requeue misuse could cause waiters to think flushes are done too early or never done. `__wt_tiered_flush_work_wait` only detects queued flush entries, not necessarily in-flight ones, so correctness depends on `flush_state` and worker protocols elsewhere. The unsafe queue-empty peek intentionally suppresses TSan noise; real concurrency protection occurs in the locked scan. Remove-local scheduling uses wall-clock seconds plus retention, so clock changes can affect timing.

## Test Signals
Tests should cover enqueue/dequeue by each type, generation-filtered flush pops, retention-filtered local-remove pops, requeue without extra dhandle acquire, removing all work for a handle, flush-state increment/decrement and waiter signaling, timeout behavior in flush wait, and concurrent producer/consumer stress under TSan.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/tiered/tiered_work.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn.c -->
# sources/storage-engines/wiredtiger/src/txn/txn.c Research

## Purpose
This file is WiredTiger's core transaction state machine. It manages transaction snapshots, oldest-id advancement, transaction configuration, commit/prepare/rollback, prepared-update resolution, checkpoint-cursor transaction objects, transaction statistics, session/global transaction lifecycle, shutdown checkpoint/rollback-to-stable coordination, eviction-blocking detection, and verbose diagnostics.

## Important APIs, Types, and Functions
- Snapshot and visibility: `__wt_txn_import_snapshot`, `__wt_txn_release_snapshot`, `__wt_txn_active`, `__wt_txn_get_snapshot`, `__wt_txn_bump_snapshot`, `__wt_txn_snapshot_save_and_refresh`, and `__wt_txn_snapshot_release_and_restore`.
- Oldest-id management: `__txn_oldest_scan` and `__wt_txn_update_oldest`.
- Configuration: `__wt_txn_config`, `__wt_txn_reconfigure`, and operation-timeout helpers.
- Prepared transaction internals: `__wt_txn_resolve_prepared_op`, `__txn_prepare_rollback_restore_hs_update`, `__txn_prepare_rollback_delete_key`, `__txn_resolve_prepared_update_chain`, and `__txn_mod_compare`.
- State transitions: `__wt_txn_commit`, `__wt_txn_prepare`, and `__wt_txn_rollback`.
- Lifecycle: `__wt_txn_init`, checkpoint-cursor init/close, `__wt_txn_release_resources`, `__wt_txn_destroy`, `__wt_txn_global_init`, `__wt_txn_global_destroy`, `__wt_txn_activity_drain`, and `__wt_txn_global_shutdown`.
- Diagnostics and pressure handling: `__wt_txn_stats_update`, `__wt_txn_is_blocking`, `__wt_verbose_dump_txn_one`, and `__wt_verbose_dump_txn`.

## Control Flow and State
Snapshots are built by scanning the global per-session shared transaction table under the transaction global rwlock. The code records active transaction ids into a sorted snapshot array, publishes pinned ids when requested, and uses generation tracking to avoid rebuilding valid snapshots. Oldest-id advancement performs a read scan, conditionally upgrades to a write lock, rescans to avoid races with sessions that have local snapshots not yet published, and then advances `oldest_id`, `last_running`, and `metadata_pinned` monotonically.

Commit first configures operation timeout and timestamps, releases snapshots after copying cursor values when needed, applies timestamps or resolves prepared updates, optionally enters the commit generation and checks stable timestamp movement, writes a log record under the visibility lock, then enters a no-fail region. After that point it frees transaction operations, releases the transaction id and snapshot state, advances snapshot generation for non-readonly commits, updates the global durable timestamp by CAS, validates prepared durable timestamp relative to stable, and may assist eviction.

Prepare sets prepare timestamp and prepared id, rejects logged/history/metadata updates, releases the snapshot, marks each update prepared, clears stale update pointers for normal btrees, flags repeated-key operations so commit/rollback resolves each key once, removes the transaction id from the global table, and sorts modifications by btree/key to improve resolution locality. Rollback releases the snapshot, aborts non-prepared updates, resolves prepared updates when needed, rolls back fast deletes and layered truncates, frees operations, and releases transaction state.

## State and Persistence Behavior
The file coordinates in-memory transaction ids, snapshots, pinned ids/timestamps, modification arrays, update-chain state, prepared ids, commit/durable/prepare/rollback timestamps, and global transaction timestamps. Durable effects occur through update-chain timestamp installation, history-store restoration for prepared resolution, transaction log calls, checkpoint/RTS during shutdown, and checkpoint-cursor snapshots. The commit path explicitly treats the window after logging as a corruption boundary where later failures panic.

## Dependencies and Integration Points
This module integrates with almost every storage subsystem: cursor and btree search, update chains, history store cursors, page modification and cache accounting, reconciliation-visible prepare states, logging, checkpoint, rollback-to-stable, eviction, statistics, metadata handles, session generations, operation timers, and disaggregated/layered table logic. It relies heavily on WiredTiger atomics and memory barriers to publish transaction ids and prepare-state transitions safely.

## Risks and Edge Cases
Prepared update resolution is the densest risk area. It must handle prepared updates only in memory, prepared updates restored from disk, older history-store versions, no older value, rollback tombstones, repeated keys, aborted reserve updates, and concurrent readers/reconciliation. Commit has a strict no-fail boundary after the log write. Snapshot and oldest-id code is race-sensitive around sessions allocating ids and read-uncommitted pinned ids. Shutdown logic changes behavior for disaggregated storage, precise checkpoint, stable timestamp use, panic/read-only/in-memory states, and debug checkpoint skipping. Eviction-blocking rollback policy differs between standalone and MongoDB builds.

## Test Signals
Coverage should include snapshot sorting/import/release, oldest-id advancement with active/pinned/metadata/checkpoint sessions, commit timestamp validation, non-prepared and prepared commit/rollback, repeated-key prepared transactions, prepared updates on disk with and without history-store fallback, rollback of prepared deletes with no committed value, transaction logging failure before and after no-fail boundary, shutdown rollback-to-stable plus checkpoint combinations, checkpoint cursor snapshots, eviction oldest-id rollback, and diagnostic dumps under active transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn_log.c -->
# sources/storage-engines/wiredtiger/src/txn/txn_log.c Research

## Purpose
This file handles transaction log record construction, commit log writes, checkpoint/file-sync log records, truncate logging, transaction operation cleanup, timestamp log operations, and human-readable printlog output.

## Important APIs, Types, and Functions
- Operation logging helpers: `__txn_op_log_row_key_check`, `__txn_op_log`, `__txn_logrec_init`, and public `__wt_txn_log_op`.
- Commit logging: `__wti_txn_log_commit`.
- Checkpoint/file sync: `__txn_log_file_sync`, `__wti_txn_checkpoint_logread`, and `__wt_checkpoint_log`.
- Timestamp logging: `__wti_txn_ts_log`.
- Truncate logging: `__wt_txn_truncate_log` and `__wt_txn_truncate_end`.
- Cleanup and printing: `__wt_txn_op_free`, `__txn_oplist_printlog`, `__txn_printlog`, and public `__wt_txn_printlog`.

## Control Flow and State
`__wt_txn_log_op` operates on the last transaction modification and appends the appropriate packed operation to the transaction's in-memory log record. Row-store operations pack keys and values/removes; column-store operations pack recnos. Modify operations are logged as modify records only when idempotent; size-changing non-idempotent modifies are logged as full puts to keep recovery safe. `__txn_logrec_init` lazily allocates the commit log record header and transaction id. Commit simply writes the accumulated log record with the transaction's sync flags.

Checkpoint logging is multi-stage. Prepare marks a full checkpoint, writes a checkpoint-start system/message record depending on log version, briefly takes the visibility write lock to ensure logged transactions are visible, and force-syncs the checkpoint LSN. Start copies the transaction snapshot into packed scratch space. Stop writes the checkpoint record containing the checkpoint LSN and snapshot, optionally updates the logging subsystem checkpoint LSN for log removal, and falls through to cleanup. File-sync checkpoint logging uses a separate `WT_LOGREC_FILE_SYNC` record unless a full checkpoint is already in progress.

## State and Persistence Behavior
This is a persistence-critical module. It determines the exact logical operations recovery replays, the transaction id associated with commit records, timestamp records used by recovery/debugging, checkpoint LSN records used to bound recovery, and truncate range records. It also frees transaction operation memory and decrements dhandle in-use counts, which affects handle lifetime after transaction completion.

## Dependencies and Integration Points
The file integrates with log packing/unpacking generated helpers, the log manager, btree/cursor state, transaction modification arrays, truncate metadata, checkpoint transaction state, visibility locks in `txn_global`, filesystem stream output, and recovery printlog infrastructure. It is called by cursor update paths, truncate paths, transaction commit, timestamp setting, checkpoint, and user-facing log printing.

## Risks and Edge Cases
Recovery idempotence is the key risk: non-idempotent modifies must be logged as full values. Row-key diagnostic checking compares the cursor key with the page/insert key and can fail hard under diagnostic validation. Truncate logging preserves original explicit cursor keys rather than potentially changed local bounds. Checkpoint cleanup must release scratch snapshot buffers on every path. Visibility lock ordering around checkpoint prepare and commit logging is essential so checkpoint LSNs reflect visible data. `__wt_txn_op_free` can be called more than once on `WT_TXN_OP_NONE`, but other operation types require correct dhandle reference balancing.

## Test Signals
Tests should cover row/column put/modify/remove logging, non-idempotent modify recovery as full put, diagnostic row-key mismatch detection, logged truncate ranges with explicit start/stop combinations, sync flag inheritance and commit-time overrides, checkpoint prepare/start/stop/cleanup sequences for old and new log versions, hot-backup and dirty-recovery conditions that suppress log removal, timestamp log records for prepared and non-prepared transactions, printlog JSON/message output, and operation free idempotence for cleared ops.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/txn/txn_log.c -->
