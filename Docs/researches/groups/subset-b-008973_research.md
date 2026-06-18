# Research Group: subset-b-008973

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered_page_log.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_layered_page_log.c

## Purpose
This file implements the connection-side disaggregated-storage page-log helpers for metadata, checkpoint metadata, and key-provider material. It is the bridge between WiredTiger checkpoint/turtle metadata and the `WT_PAGE_LOG` extension interface used by disaggregated storage and layered tables. It also owns the serialization, validation, and in-memory queueing rules for encryption key material that must be persisted into the page log.

## Important APIs, Types, and Functions
Important exported entry points include `__wti_layered_get_disagg_checkpoint`, `__wti_disagg_load_crypt_key`, `__wti_disagg_parse_crypt_meta`, `__wti_disagg_pending_crypt_key_clear`, `__wti_disagg_set_crypt_key`, `__wt_disagg_put_crypt_helper`, `__wti_disagg_fetch_shared_meta`, `__wt_disagg_put_checkpoint_meta`, and `__wt_disagg_parse_meta`. Key local helpers are `__disagg_get_page`, `__disagg_put_page`, `__disagg_validate_crypt`, `__disagg_set_crypt_header`, `__disagg_select_pending_crypt_key`, `__disagg_prune_pending_crypt_keys`, `__disagg_get_meta`, `__disagg_put_meta`, `__disagg_parse_legacy_meta`, `__disagg_parse_meta`, and `__disagg_parse_version_and_check`.

The main data structures are `WT_DISAGGREGATED_STORAGE`, `WT_PAGE_LOG_HANDLE`, `WT_PAGE_LOG_GET_ARGS`, `WT_PAGE_LOG_PUT_ARGS`, `WT_DISAGG_METADATA`, `WT_DISAGG_CHECKPOINT_META`, `WT_CRYPT_KEYS`, `WT_CRYPT_HEADER`, and `WT_DISAGG_PENDING_CRYPT_KEY`.

## Control Flow and Behavior
Page-log reads and writes flow through `__disagg_get_page` and `__disagg_put_page`, both of which require the connection checkpoint lock. Reads retry up to 100 times to tolerate page materialization delay and fail with `EIO` after repeated misses. Writes chain the previous LSN via `backlink_lsn`, update the per-page last-LSN array, and optionally return the new LSN.

Encryption-key load starts from checkpoint metadata: `__wti_disagg_load_crypt_key` parses page ID/LSN metadata, reads the key-provider page, validates checksum/header/version/signature, points `WT_CRYPT_KEYS` at the payload, calls `key_provider->load_key`, and prunes queued pushed keys up to the loaded timestamp. Key persistence happens in `__wt_disagg_put_crypt_helper`, which either selects a queued push-mode key at or before the checkpoint timestamp or asks pull-mode providers via `get_key`; it then prepends a `WT_CRYPT_HEADER`, writes the key page, and calls `on_key_update` with either LSN or error.

Checkpoint metadata persistence is handled by `__wt_disagg_put_checkpoint_meta`: it captures checkpoint root, checkpoint timestamp, oldest timestamp, schema epoch, largest file ID, optional key-provider metadata, and checksum, writes the metadata page, then atomically updates in-memory last-checkpoint fields. Metadata parsing supports both the legacy newline format and current config format, with version/compatible-version validation before parsing current fields.

## State and Persistence
Persistent state is stored in page-log pages for checkpoint metadata and key-provider payloads. In-memory state includes `last_metadata_page_lsn`, `last_key_provider_page_lsn`, `last_checkpoint_meta_lsn`, `last_checkpoint_timestamp`, `last_checkpoint_oldest_timestamp`, `last_checkpoint_schema_epoch`, `last_checkpoint_meta_checksum`, `last_checkpoint_root`, `num_meta_put`, and the pending key tail queue. Durable metadata includes `checkpoint`, `timestamp`, `oldest_timestamp`, `schema_epoch`, `largest_file_id`, optional `key_provider`, and checksum tracked separately in checkpoint metadata.

## Dependencies and Integration Points
The file depends on WiredTiger config parsing, scratch buffers, checksums, metadata checkpoint readers, timestamp parsing/formatting, checkpoint/schema locks, key-provider callbacks, disaggregated connection configuration, and the page-log extension API. It is called from checkpoint, recovery/reconfigure, disaggregated metadata fetch, key-provider rotation, and layered/disaggregated tests.

## Risks
Important risks are checkpoint-lock misuse, corrupt or incompatible metadata silently accepted, bad byte swapping or checksum handling for crypt headers, stale LSN arrays producing broken backlink chains, push-mode queued keys being selected after lock release, and failures after the metadata page write but before in-memory bookkeeping. The code intentionally treats the page-log metadata write as the last fallible operation in `__wt_disagg_put_checkpoint_meta`.

## Test Signals
Useful signals include unit-test hooks under `HAVE_UNITTEST` for crypt header validation and metadata version parsing, disaggregated storage tests that fetch complete checkpoints, key-provider crash-trigger tests around before/during/after rotation, metadata corruption checksum tests, and compatibility tests for legacy/current checkpoint metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered_page_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered_table_manager.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_layered_table_manager.c

## Purpose
This file manages the connection-level registry of currently open layered tables. The manager records stable, ingest, and layered URIs by ingest ID so other layered-table/disaggregated paths can discover open layered tables while handles are alive.

## Important APIs, Types, and Functions
The public functions are `__wti_layered_table_manager_init`, `__wt_layered_table_manager_add_table`, `__wt_layered_table_manager_remove_table`, and `__wti_layered_table_manager_destroy`. The local helper `__layered_table_manager_remove_table_inlock` removes one entry while the manager lock is held. Important types are `WT_LAYERED_TABLE_MANAGER`, `WT_LAYERED_TABLE_MANAGER_ENTRY`, and `WT_LAYERED_TABLE`.

## Control Flow and Behavior
Initialization asserts the manager is not already initialized, creates `layered_table_lock`, sizes the `entries` array to `conn->next_file_id + 1000` under the schema lock, sets `WT_CONN_SERVER_LAYERED`, and marks the manager initialized. Adding a table requires a layered dhandle context, allocates an entry, borrows URI pointers from the layered handle, grows the array if the ingest ID exceeds the current capacity, panics on duplicate registration, increments layered-table manager stats, and installs the entry under the spin lock. Removal is idempotent during shutdown: if initialized, it locks, frees the entry at the ingest ID, decrements stats, and clears the slot. Destroy clears the server flag, removes every remaining entry, frees the array, resets counters, marks the manager uninitialized, unlocks, and destroys the spin lock.

## State and Persistence
The manager is entirely in-memory. It does not persist table registrations; it relies on dhandle open/close lifecycle to add and remove entries. Entry URI strings are not copied, so their validity depends on the layered dhandle outliving the manager entry.

## Dependencies and Integration Points
This file integrates with data-handle open/close paths, layered table handles, connection server flags, schema locking for initial file-ID sizing, connection statistics, and verbose layered logging. `conn_open.c` destroys the manager after closing data handles, which matches the borrowed URI lifetime assumption.

## Risks
The main risks are incorrect ingest IDs causing array growth mistakes, duplicate opens overwriting manager entries, borrowed URI pointers surviving longer than the layered dhandle, and removal races around shutdown. The code assumes entries are protected by `layered_table_lock` and that removal after handle close is safe because checkpoints have already covered writes to the layered table.

## Test Signals
Test coverage should observe layered table open/close accounting, duplicate-open diagnostics, clean shutdown with open layered handles, and step-up/drain flows that depend on layered handles remaining discoverable while ingest tables need processing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_layered_table_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_load_control.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_load_control.c

## Purpose
This file implements connection-level load-control configuration and load percentage calculation. Load control maps cache pressure to read and write load values so upper layers can reject work once configured thresholds are exceeded.

## Important APIs, Types, and Functions
The public functions are `__wti_conn_load_control_config`, `__wt_conn_calc_read_load`, and `__wt_conn_calc_write_load`. Local helpers are `__conn_load_control_configure` and `__conn_calc_load_pct`. Important state lives in `WT_CONNECTION_LOAD_CONTROL` and eviction/cache fields such as `conn->cache_size`, `evict->eviction_trigger`, and `evict->eviction_dirty_trigger`.

## Control Flow and Behavior
Configuration reads `load_control.enable` and sets `WT_CONN_LOAD_CONTROL` when enabled. It reads `load_control.control_threshold`, clamps the stored threshold to 200, and recalculates read/write maximum byte thresholds. Read load maps current cache bytes in use to the configured eviction trigger threshold. Write load maps dirty cache bytes to the eviction dirty trigger threshold. Both calculations saturate at 200% and update connection statistics.

## State and Persistence
State is volatile connection configuration: `read_load_max`, `write_load_max`, `control_threshold`, `read_load`, `write_load`, and the load-control enabled flag. There is no on-disk persistence. Reconfiguration recalculates thresholds because they depend on both load-control and eviction/cache settings.

## Dependencies and Integration Points
The file depends on configuration parsing, atomic stores, cache byte counters, eviction configuration, and connection stats. It is initialized in `__wti_connection_open` after cache/eviction setup and reconfigured from `__wti_conn_reconfig` after cache and eviction reconfiguration.

## Risks
Risks include stale thresholds if eviction or cache size changes without reconfiguration, integer truncation from double-based percentage thresholds, disabled load-control leaving old load values visible in stats, and threshold semantics changing if eviction trigger defaults change.

## Test Signals
Relevant signals are configuration tests for enable/disable and threshold clamping, stats for `read_load`/`write_load`, and workloads that drive clean or dirty cache pressure past the configured activation threshold.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_load_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_open.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_open.c

## Purpose
This file orchestrates major connection open, worker startup, and connection close ordering. It wires together the cache, eviction, transaction, recovery, logging, metadata, disaggregated storage, tiered storage, statistics, sweep, checkpoint, prefetch, and cleanup subsystems.

## Important APIs, Types, and Functions
The main entry points are `__wti_connection_open`, `__wti_connection_close`, and `__wti_connection_workers`. They operate on `WT_CONNECTION_IMPL`, its default/internal sessions, connection flags, server flags, and subsystem-owned state.

## Control Flow and Behavior
Open allocates the session array, opens the default internal session, publishes the initialized connection pointer with a release barrier, creates cache/eviction/shared-cache state, initializes transaction and rollback-to-stable state, records dhandle stat sizing, and configures load control after cache and eviction are available.

Worker startup begins with checkpoint reconciliation threads and statistics logging, detects disaggregated mode from `disaggregated.page_log`, starts tiered storage unless disaggregated is enabled, creates the log manager, configures page history, runs recovery, starts live restore, initializes metadata tracking, configures disaggregated storage, opens the history store, opens logging, starts eviction, sweep, background compact, capacity, checkpoint, prefetch, and checkpoint cleanup.

Close sets `WT_CONN_CLOSING`, restores data-handle access on the default session, then shuts down subsystems in dependency order: page history, live restore, background compact, checkpoint, stats, tiered, sweep, prefetch, parallel checkpoint, eviction threads, capacity, data handles, metadata tracking, block cache, layered table manager, log manager, disaggregated storage, extensions, shared cache, eviction, cache, transactions, files, optrack, backup metadata, sessions, file system, dynamic libraries, compiled config, and finally the connection object.

## State and Persistence
This file coordinates both volatile and persistent state. It ensures recovery runs before history-store creation and before eviction threads, ensures logging is open before operations that may commit, and checkpoints log state on close when logging recovery is complete. It also removes backup temp state and releases lock/optrack files.

## Dependencies and Integration Points
It is the high-level integration point for nearly every connection subsystem. Ordering constraints are encoded directly in the call sequence, including disaggregated/tiered mutual exclusion, metadata/disaggregated/history-store order, and eviction shutdown after all higher-level servers stop.

## Risks
Risks are mostly ordering regressions: starting eviction before history store exists, running tiered storage in disaggregated mode, closing data handles before worker threads stop, destroying cache before shared-cache disconnect, closing log manager before checkpoint-log stop, or leaving sessions and hazard/stash state allocated on close.

## Test Signals
Signals include connection open/close smoke tests, recovery tests, leak checks, tiered/disaggregated mode combinations, logging shutdown tests, backup cleanup tests, and tests that enable optional servers such as stats, sweep, prefetch, checkpoint, and page history.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_page_history.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_page_history.c

## Purpose
This file implements debug-mode page history tracking. When enabled, it records read and eviction counts for pages with disaggregated page IDs and periodically reports the most reread and most evicted pages.

## Important APIs, Types, and Functions
Public entry points are `__wti_conn_page_history_config`, `__wti_conn_page_history_destroy`, `__wt_conn_page_history_track_evict`, and `__wt_conn_page_history_track_read`. Local helpers include report formatting, top-N comparators, `__conn_page_history_report`, and the reporter thread `__conn_page_history_reporter`. Key types are `WT_PAGE_HISTORY`, `WT_PAGE_HISTORY_ITEM`, `WT_PAGE_HISTORY_KEY`, and `WT_HASH_MAP`.

## Control Flow and Behavior
Configuration reads `debug_mode.page_history`. Enabling lazily initializes a large hash map, allocates a condition variable, opens a dedicated internal session, clears shutdown, and starts a reporter thread. Disabling stops the reporter but intentionally keeps the rest of the state alive to avoid synchronization hazards with concurrent track calls.

Track-read increments global read counters, ignores local pages without disaggregated info, keys pages by table ID and page ID, records first/last read timestamps and global read counters, increments per-page reads, and increments reread count after the first read. Track-evict similarly counts global, local, and no-page-ID evictions and increments per-page eviction counts. The reporter wakes every second and emits a report every 30 wakeups, scanning the hash map under bucket locks and maintaining top-five arrays for reads and evictions.

## State and Persistence
All state is in memory and debug-only. It tracks global read/evict counters, local/no-page-ID counters, rereads, a hash map of page history items, reporter session/thread/condition state, and shutdown/enabled flags. It does not persist page history across restarts.

## Dependencies and Integration Points
The tracker depends on disaggregated page IDs in `page->disagg_info`, btree table IDs from `S2BT(session)->id`, hash-map locking, atomics/barriers, internal sessions, and connection verbose/message output. It is configured during worker startup and reconfiguration, and destroyed early in connection close.

## Risks
Risks include high memory use from a 10-million-entry hash map, overhead on every tracked read/evict, races when disabling while sessions are still tracking, relying on disaggregated page IDs only, and report sorting while holding hash bucket locks. The code keeps state alive after disable specifically to reduce use-after-free risk.

## Test Signals
Signals include debug-mode configuration tests, periodic report output, counters for local versus disaggregated pages, top-N output correctness, clean thread shutdown on reconfigure/close, and stress tests that read/evict pages while toggling the feature.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_page_history.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_prefetch.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_prefetch.c

## Purpose
This file implements the connection prefetch queue and prefetch worker thread group. It lets traversal paths enqueue disk refs for asynchronous page reads while protecting refs and internal pages from eviction until workers finish.

## Important APIs, Types, and Functions
Public functions are `__wti_conn_prefetch_init`, `__wti_conn_prefetch_destroy`, `__wti_prefetch_create`, `__wt_conn_prefetch_queue_push`, `__wt_conn_prefetch_clear_tree`, and `__wti_prefetch_destroy`. Worker helpers are `__prefetch_thread_chk` and `__prefetch_thread_run`. Important types are `WT_CONN_PREFETCH`, `WT_PREFETCH_QUEUE_ENTRY`, `WT_THREAD_GROUP`, `WT_REF`, and `WT_BTREE`.

## Control Flow and Behavior
Initialization sets up the queue and spin lock. Create reads `prefetch.available`; if unavailable it does not start workers. If available, it sets `WT_CONN_SERVER_PREFETCH` and creates a fixed-size thread group. Workers wait on the group condition, pop queued entries under the prefetch lock, skip and clear entries under clean-cache pressure, increment the owning btree `prefetch_busy` counter, prefetch via `__wt_prefetch_page_in` under the saved dhandle, clear `WT_REF_FLAG_PREFETCH`, decrement busy, and ignore benign `WT_NOTFOUND`/`WT_RESTART`.

Queue push avoids adding work under clean-cache pressure or when tree eviction is disabled. It deduplicates by `WT_REF_FLAG_PREFETCH`, CAS-locks disk refs before queueing to prevent eviction/free races, sets the prefetch flag, restores ref state, appends the queue entry, increments the queue count, unlocks, and signals workers. Clear-tree removes queued entries for one dhandle or all dhandles, clears flags, decrements queue count, and for per-tree clearing waits until `prefetch_busy` drains.

## State and Persistence
State is volatile: the queue, lock, queue count, prefetch availability, server flag, thread group, and per-btree `prefetch_busy`. No data is persisted; prefetch is a performance feature.

## Dependencies and Integration Points
The file depends on eviction pressure checks, ref state transitions, dhandle lifetime, btree eviction-disable flags, thread groups, timing stress hooks, TSAN-suppressed counters, and statistics. It is started from connection workers and stopped before data handles and eviction are destroyed.

## Risks
The critical risks are ref lifetime races, missing flag cleanup on skipped/error paths, queue entries referencing closing dhandles, cache pressure causing prefetch to worsen eviction, and deadlock if per-tree close waits while workers cannot drain. The code uses ref CAS, prefetch flags, `prefetch_busy`, and queue clearing to mitigate those hazards.

## Test Signals
Signals include prefetch statistics for skipped conditions, queue count returning to zero after clear/destroy, eviction/verify corruption paths that stop prefetch safely, stress timing flags, and tests that close trees while prefetch workers are active.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_prefetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_reconfig.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_reconfig.c

## Purpose
This file implements connection reconfiguration support plus related connection-level configuration helpers for compatibility version, operation tracking, and statistics selection.

## Important APIs, Types, and Functions
Important exported functions are `__wti_conn_compat_config`, `__wti_conn_optrack_setup`, `__wti_conn_optrack_teardown`, `__wti_conn_statistics_config`, and `__wti_conn_reconfig`. Local helper `__conn_compat_parse` parses release strings. Important state includes `conn->cfg`, `compat_version`, `compat_req_min`, `compat_req_max`, `optrack`, `stat_flags`, and `reconfig_lock`.

## Control Flow and Behavior
Compatibility parsing accepts major.minor or major.minor.patch strings and rejects versions newer than the library. Compatibility configuration handles default current-version mode, upgrade/downgrade quiescence checks, required min/max checks, saved turtle compatibility validation, and turtle rewrite on reconfigure under the turtle or live-restore path.

Operation tracking setup stores the configured path at open, rejects read-only mode, creates a process-ID-qualified map file, initializes its spin lock and dummy-session buffer, and sets `WT_CONN_OPTRACK`. Teardown destroys the spin lock, closes the map file, frees buffers, and optionally frees the path on close.

Statistics configuration parses mutually exclusive `none`, `fast`, and `all`, then optional `cache_walk`, `tree_walk`, and `clear`, with a live-restore guard that prevents disabling stats.

`__wti_conn_reconfig` serializes with `reconfig_lock`, replaces `cfg[0]` with current connection config, detects a fast path for disaggregated-only updates, and otherwise runs all subsystem reconfigurers in an explicit order. It then merges config back into `conn->cfg`, excluding transient disaggregated checkpoint metadata and last-materialized LSN.

## State and Persistence
Reconfig updates volatile connection state and, for compatibility changes, rewrites turtle metadata. Operation tracking creates/removes files. Statistics flags are connection state. The saved connection config string is replaced atomically enough under `reconfig_lock`.

## Dependencies and Integration Points
This file integrates with transaction quiescence, metadata turtle rewriting, live restore, block cache, optrack, page history, stats, cache, eviction, shared cache, load control, capacity/checkpoint servers, debug/diagnostics, disaggregated storage, history store, log manager, statlog, tiered storage, sweep, timing stress, JSON, verbose, and rollback-to-stable.

## Risks
Risks include reconfiguration order dependencies, accidentally preserving transient disaggregated config, changing compatibility while operations/checkpoints are active, restarting statlog too aggressively, operation-tracking resource leaks on partial setup, and fast-path disaggregated updates skipping a dependent history-store reconfiguration when more than last-materialized LSN changes.

## Test Signals
Signals include compatibility upgrade/downgrade tests, quiescence enforcement, turtle rewrite behavior, reconfigure idempotence, disaggregated fast-path reconfig tests, statistics option validation, live-restore statistics guard, and operation tracking enable/disable resource cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_reconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_stat.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_stat.c

## Purpose
This file initializes connection statistics and implements the optional statistics log server. It periodically writes connection and selected file statistics in text or JSON format and can also emit one final sample on close.

## Important APIs, Types, and Functions
Public entry points are `__wt_conn_stat_init`, `__wti_statlog_create`, and `__wti_statlog_destroy`. Important helpers include `__stat_config_discard`, `__statlog_config`, `__statlog_print_header`, `__statlog_print_table_name`, `__statlog_print_footer`, `__statlog_dump`, `__statlog_apply`, `__statlog_log_one`, `__statlog_on_close`, `__statlog_server`, and `__statlog_start`.

## Control Flow and Behavior
`__wt_conn_stat_init` refreshes cache, checkpoint timer, eviction, and transaction stats, then snapshots open-file, open-btree, open-cursor, dhandle, checkpoint dhandle, and reconciliation stash counters into connection stats.

Statlog create ignores read-only connections. It tears down any previous server or stale config, parses `statistics_log.wait`, `json`, `on_close`, path, source list, and timestamp format, and starts a dedicated internal session/thread if wait is nonzero. The server waits on a condition for the configured interval, then calls `__statlog_log_one` while enabled. Each sample opens or rotates the log file based on strftime path expansion, formats the timestamp, writes JSON headers if needed, dumps `statistics:` for the connection, and optionally walks open btree handles matching configured `file:` source prefixes after recovery completes.

Destroy clears the server flag, signals and joins the thread, destroys the condition, optionally logs on close, discards config and closes the log stream, and closes the statlog session.

## State and Persistence
Statistics counters live in memory; statlog output is persistent in configured files. State includes `conn->stat_log.path`, `format`, `fs`, `sources`, `stamp`, `usecs`, `session`, `cond`, `tid`, `tid_set`, and JSON table-state. Reconfiguration discards and rebuilds this state.

## Dependencies and Integration Points
The file uses statistics cursors, config parsing, file-system open/append/flush, local time/strftime, btree apply, recovery-complete flag, server flags, condition variables, internal sessions, and connection stat macros. It is started early in worker startup so other optional servers can observe statistics settings.

## Risks
Risks include malformed JSON grouping when statistic descriptions lack expected prefixes, statlog source races with intermittently removed objects, path/timestamp strftime failures, restarting statlog during reconfigure while users expect continuity, and on-close logging while a server is still running. The code handles busy/notfound stats cursors as nonfatal.

## Test Signals
Signals include text and JSON statlog files, source filtering for file objects, log rotation by path format, on-close output, read-only no-op behavior, reconfigure restart behavior, and valid JSON with both connection and table sections.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_sweep.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_sweep.c

## Purpose
This file implements the handle sweep server. It marks idle data handles with a time of death, closes clean open handles, discards dead btrees, removes unreferenced handles from the connection list, and emits diagnostics for sessions that have not swept cursor/dhandle references.

## Important APIs, Types, and Functions
Public functions are `__wti_sweep_config`, `__wti_sweep_create`, and `__wti_sweep_destroy`. Core helpers include `__sweep_mark`, `__sweep_expire`, `__sweep_discard_trees`, `__sweep_remove_handles`, `__sweep_remove_one`, `__sweep_expire_one`, `__sweep_close_dhandle_locked`, `__sweep_file_dhandle_check_and_reset_tod`, `__sweep_check_session_sweep`, and the server thread `__sweep_server`. Important macros/state include `WT_DHANDLE_CAN_DISCARD`, `WT_DISAGG_OUTDATED_GRACE_SECS`, dhandle flags, `conn->sweep`, and `conn->dhqh`.

## Control Flow and Behavior
Configuration sets idle time to zero for in-memory mode, otherwise reads file-manager close idle time, scan interval, and minimum handle count. Create sets `WT_CONN_SERVER_SWEEP`, opens an internal session with wait and ignore-cache-size flags, allocates a condition, and starts the server.

The server waits for interval or signal, skips full sweeps during checkpoint handle gathering, marks idle non-metadata handles, expires handles when above the minimum or in disaggregated mode, discards pages from dead open handles, removes closed unreferenced handles, checks stale session sweep activity, and in disaggregated leader mode marks the shared disk cache dead after the readonly grace window. Table handles get extra checks so simple table handles stay alive while their file dhandle exists. Layered and history-store handles are not marked for normal idle sweep.

## State and Persistence
Sweep state is in memory: dhandle `timeofdeath`, flags, reference counts, open counts, server session/thread/condition, sweep config, and session warning booleans. It changes persistent effects indirectly by closing/discarding handles and removing local dhandle structures, not by writing metadata.

## Dependencies and Integration Points
The file depends on handle-list locks, table locks, dhandle write locks, checkpoint state, btree modified state, connection dhandle close/discard functions, session array walks, disaggregated shared disk cache state, and statistics. It integrates with connection close and reconfigure through create/destroy/config calls.

## Risks
Risks include closing a handle still needed by active sessions, table/file handle ordering races, interference with checkpoint handle gathering, deadlocks from lock order, retaining too many handles when session references are not swept, and disaggregated outdated checkpoint handles being closed before the shared disk cache reuse window expires.

## Test Signals
Signals include sweep statistics for time-of-death, expired close, dead close, remove, ref skips, checkpoint skips, and no-session-sweep warnings. Behavioral tests should cover table/file dhandle retention, history-store/layered exclusions, disaggregated outdated checkpoint cleanup, and clean shutdown of the sweep server.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_sweep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_tiered.c -->
# sources/storage-engines/wiredtiger/src/conn/conn_tiered.c

## Purpose
This file implements connection-level tiered storage worker infrastructure. It processes queued work to copy flushed local objects to shared storage, run storage-source post-flush completion, and remove local objects after retention.

## Important APIs, Types, and Functions
Public entry points are `__wti_conn_tiered_init`, `__wti_conn_tiered_destroy`, `__wti_tiered_storage_create`, and `__wti_tiered_storage_destroy`. Core helpers include `__tier_storage_remove_local`, `__tier_flush_meta`, `__tier_release_local_object`, `__tier_do_operation`, `__tier_operation`, `__tier_storage_finish`, `__tier_storage_copy`, `__tier_storage_remove`, and `__tiered_server`. Key types are `WT_CONN_TIERED`, `WT_TIERED_WORK_UNIT`, `WT_TIERED`, `WT_STORAGE_SOURCE`, `WT_FILE_SYSTEM`, `WT_BM`, and metadata tracking structures.

## Control Flow and Behavior
Connection-tiered init creates the work queue and locks. Create skips the tiered server when disaggregated storage is configured, allocates flush/storage conditions, sets `WT_CONN_SERVER_TIERED`, opens a dedicated internal session, sets the first-flush flag, and starts the server.

The server waits for interval or signal, then runs copy, finish, and remove phases. Copy waits for a checkpoint after flush completion, uses checkpoint generation to avoid processing work units from tables added during an active checkpoint, and calls `__tier_operation` for eligible flush work. A flush operation builds local/object names, prefixes object names with bucket prefix, calls `storage_source->ss_flush`, then under checkpoint and schema locks updates metadata by removing the local file entry and adding flush time/timestamp to the object entry. It releases the local object through the block manager, queues a flush-finish work unit, and queues future local removal. Finish calls `ss_flush_finish`. Remove-local checks retention time, removes local object files if no handle keeps them open, or requeues with a new deadline.

## State and Persistence
Volatile state includes work queues, locks, conditions, server thread/session, interval, first-flush and flush-checkpoint-complete flags. Persistent state changes happen in metadata: local file metadata is removed after successful flush, object metadata records flush time and timestamp, and local files may be removed after retention. Unfinished work is intentionally recoverable on startup rather than forced at shutdown.

## Dependencies and Integration Points
The file depends on tiered naming helpers, metadata tracking, checkpoint/schema locks, block-manager object switching, storage-source flush APIs, bucket filesystem, condition variables, timing stress flags, and connection worker startup. It is mutually excluded with disaggregated storage in `conn_open.c`.

## Risks
Risks include metadata becoming inconsistent if flush succeeds but metadata update fails, dropped handles while work units still reference tiered structures, network/storage-source timeouts, local removal while a file handle is still open, generation races with checkpoint, and shutdown with queued work that must be recovered later.

## Test Signals
Signals include successful flush_tier metadata transitions, storage-source `ss_flush`/`ss_flush_finish` calls, local object retention/removal behavior, restart recovery of unfinished work, disaggregated mode not starting tiered server, and timing-stress tests around flush-finish.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/conn/conn_tiered.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_backup.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_backup.c

## Purpose
This file implements the main backup cursor, including full hot backup, targeted backup, query-id backup cursors, export backup cursors, incremental backup state management, duplicate backup cursors, and backup metadata file generation.

## Important APIs, Types, and Functions
Public functions include `__wt_verbose_dump_backup`, `__wt_backup_set_blkincr`, `__wt_backup_destroy`, `__wt_backup_open`, `__wt_backup_file_remove`, and `__wt_curbackup_open`. Important local functions are `__curbackup_next`, `__curbackup_reset`, `__curbackup_close`, `__backup_free`, `__backup_add_id`, `__backup_find_id`, `__backup_log_append`, `__backup_config`, `__backup_query_setup`, `__backup_start`, `__backup_stop`, `__backup_all`, `__backup_list_uri_append`, and `__backup_list_append`.

Key structures and flags are `WT_CURSOR_BACKUP`, `WT_BLKINCR`, `WT_CONN_INCR_BACKUP`, `WT_CURBACKUP_LOCKER`, `WT_CURBACKUP_DUP`, `WT_CURBACKUP_INCR`, `WT_CURBACKUP_FORCE_STOP`, `WT_CURBACKUP_QUERYID`, `WT_CURBACKUP_EXPORT`, `WT_BLKINCR_VALID`, `WT_BLKINCR_INUSE`, and `WT_BLKINCR_FULL`.

## Control Flow and Behavior
Opening a backup cursor allocates and initializes a `WT_CURSOR_BACKUP`, handles special URIs (`backup:query_id`, `backup:export`), rejects non-export backup under tiered storage, and starts backup under checkpoint and schema locks for top-level cursors. `__backup_start` rejects in-memory mode, serializes hot backups, handles incremental `force_stop` early, sets the hot-backup flag, optionally creates the temporary backup metadata file, parses backup config, builds target/log/full lists, appends standard WiredTiger files, syncs and renames the temp file, and publishes the list under the hot-backup lock.

`__backup_config` handles incremental enable/granularity, consolidate, duplicate incremental file, source ID, new ID, target lists, log targets, and incompatibility rules. Full backups append active log files before metadata object lists to choose a safe checkpoint/log ordering. `__curbackup_next` returns successive file names as keys and advances parallel config entries for incremental backup. Close handles duplicate cursor cleanup, force-stop destruction, forced checkpoints for incremental metadata visibility, backup file removal, export-file removal, and clearing the connection hot-backup state.

## State and Persistence
Persistent backup state lives in metadata `checkpoint_backup_info` and backup files `WiredTiger.backup`, `WiredTiger.backup.tmp`, `WiredTiger.backup.metadata`, and export backup output. Incremental ID/granularity state is restored from the metadata file on open into `conn->incr_backups` and `conn->incr_granularity`. Volatile state includes open backup cursor flags, `conn->backup.start`, `conn->backup.list`, session backup flags, duplicate cursor flags, and per-cursor lists.

## Dependencies and Integration Points
This file depends on checkpoint/schema/hot-backup locks, metadata scans, schema worker, log manager backup file enumeration, filesystem rename/sync/remove, live-restore metadata cleanup, cursor initialization, tiered storage restrictions, and incremental duplicate cursor support in `cur_backup_incr.c`.

## Risks
Risks include inconsistent backup metadata if temp file handling or rename fails, checkpoint deletion racing with backup start/stop, incremental IDs left in-use on error, incompatible log/incremental/target combinations, stale incremental metadata reappearing without forced checkpoint after stop, and assumptions that metadata `file:` entries map one-to-one to physical files.

## Test Signals
Signals include full backup file lists, target backup object expansion, log backup behavior with log removal disabled/enabled, query-id output, incremental ID restore from metadata, force-stop cleanup plus checkpoint, duplicate cursor restrictions, backup temp file cleanup, and tiered-storage export behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_backup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_backup_incr.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_backup_incr.c

## Purpose
This file implements duplicate backup cursors for block-based incremental backup. Given a file selected by the primary backup cursor, it returns either whole-file copy ranges or modified block ranges derived from checkpoint backup metadata.

## Important APIs, Types, and Functions
Public functions are `__wt_backup_load_incr`, `__wti_curbackup_free_incr`, and `__wti_curbackup_open_incr`. Local helpers are `__curbackup_incr_blkmod` and `__curbackup_incr_next`. Important state is held in `WT_CURSOR_BACKUP`: `incr_src`, `incr_file`, `incr_cursor`, `cfg_current`, `bitstring`, `granularity`, `nbits`, `offset`, `bit_offset`, and flags such as `WT_CURBACKUP_INCR_INIT`, `WT_CURBACKUP_FORCE_FULL`, `WT_CURBACKUP_RENAME`, `WT_CURBACKUP_CKPT_FAKE`, `WT_CURBACKUP_HAS_CB_INFO`, `WT_CURBACKUP_COMPRESSED`, and `WT_CURBACKUP_CONSOLIDATE`.

## Control Flow and Behavior
`__wti_curbackup_open_incr` converts a duplicate backup cursor into an incremental range cursor by replacing its `next` method, inheriting the source incremental ID and current metadata config from the primary cursor, forcing full copies for WiredTiger-owned files or source IDs marked full, inheriting consolidation mode, and opening a file cursor on the target file when range metadata can be used.

`__curbackup_incr_next` returns one key per full file or modified range. If no btree cursor exists or the file is force-full/rename, it returns a `WT_BACKUP_FILE` key with offset 0 and file size, then reports `WT_NOTFOUND` on the next call. Otherwise it lazily loads checkpoint backup info via `__curbackup_incr_blkmod`, which parses `checkpoint_backup_info` for the source ID, detects compression, fake checkpoints, rename markers, granularity, bit count, base offset, and hex-encoded modified-block bitstrings. Iteration scans the bitstring for set bits and returns `WT_BACKUP_RANGE` keys; consolidation merges contiguous set bits into one returned range while still counting every block in stats.

## State and Persistence
Persistent inputs are per-file metadata fields, especially `checkpoint_backup_info` and block modification bitstrings. Cursor state is volatile and advances through `bit_offset`. Full-copy fallback uses filesystem size. The code does not write metadata; it interprets metadata produced by checkpoint/backup machinery.

## Dependencies and Integration Points
The file depends on the main backup cursor, metadata checkpoint parsing, config parsing, file cursor opening, filesystem size calls, log filename handling, statistics, btree dhandles, and cursor API macros.

## Risks
Risks include corrupted bitstrings, mismatch between `nbits` and decoded bytes, stale `cfg_current`, incorrect full-copy fallback for renamed/new files, cursor-cache interaction when opening internal file cursors, and accidentally returning compressed/uncompressed stats under the wrong dhandle.

## Test Signals
Signals include full-file keys for WiredTiger/log/renamed/new fake-checkpoint files, range keys for modified blocks, consolidated contiguous ranges, `WT_NOTFOUND` for unchanged files, corrupted modified block list errors, and correct backup block statistics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_backup_incr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_bulk.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_bulk.c

## Purpose
This file implements bulk cursor insert behavior for row-store and variable-length column-store btrees. Bulk cursors only support insert and close, and they optimize loading by assuming single-threaded, ordered, not-yet-visible input.

## Important APIs, Types, and Functions
Public functions are `__wti_curbulk_init` and `__wti_curbulk_close`. Local insert functions are `__curbulk_insert_var`, `__curbulk_insert_row`, `__curbulk_insert_row_skip_check`, plus error helpers `__bulk_col_keycmp_err` and `__bulk_row_keycmp_err`. Important types are `WT_CURSOR_BULK`, `WT_CURSOR_BTREE`, `WT_BTREE`, and scratch `WT_ITEM` buffers.

## Control Flow and Behavior
Initialization disables unsupported cursor methods, selects the insert method based on btree type and optional row-store sort-check skipping, marks the first insert, initializes record number state, allocates the `last` scratch buffer, and calls `__wt_bulk_init`.

Variable-length column inserts use append mode to synthesize sequential record numbers or require explicit increasing record numbers. They coalesce consecutive identical values by increasing the RLE count, emit skipped records as deleted runs, save the current value into `last`, and call `__wt_bulk_insert_var` when the previous run must be flushed. Row-store inserts require key/value, compare each key against the previous key with the btree collator unless sort-check skipping is configured, save the key, and call `__wt_bulk_insert_row`. Close wraps up the bulk load with `__wt_bulk_wrapup`, decrements the bulk cursor stat only on success, and frees the scratch buffer.

## State and Persistence
Bulk cursor state is transient until close: previous key/value, `first_insert`, `recno`, and RLE count. Persistent table contents are created through the underlying bulk-load machinery, and the data is not visible until the bulk cursor is closed successfully.

## Dependencies and Integration Points
The file depends on cursor API macros, key/value validation, btree type/collator, lower-level bulk insert/wrapup APIs, connection/data-source statistics, and scratch-buffer allocation.

## Risks
Risks include corruption from out-of-order keys when checks are skipped, incorrect RLE handling for zero-length values, record-number gaps not being represented as deletes, decrementing cursor stats only on successful close, and unsupported btree types falling through without an insert handler.

## Test Signals
Signals include ordered row bulk load success, out-of-order row/column errors, append-mode column load, skipped column records becoming deleted records, RLE compression for repeated values, skip-sort-check behavior, and close/wrapup error handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_bulk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_config.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_config.c

## Purpose
This small file implements the `config:` cursor wrapper. It allocates a cursor with string key/value formats and delegates ordinary key/value accessor methods while making traversal and mutation unsupported.

## Important APIs, Types, and Functions
The public entry point is `__wt_curconfig_open`. The close method is `__curconfig_close`. The cursor type is `WT_CURSOR_CONFIG`, initialized with `WT_CURSOR_STATIC_INIT`.

## Control Flow and Behavior
Open allocates a `WT_CURSOR_CONFIG`, installs a static method table, sets the session and `S` key/value formats, and calls `__wt_cursor_init`. The method table supports get/set key/value and raw key/value helpers, no-op reset, checkpoint ID, and close; next, prev, search, insert, update, remove, reserve, reconfigure, bound, cache, and reopen are unsupported. Close runs through the cursor API macro and calls `__wt_cursor_close`.

## State and Persistence
The cursor owns only normal cursor lifetime state. It does not persist anything by itself; it exposes configuration data through cursor infrastructure determined elsewhere.

## Dependencies and Integration Points
The file depends on cursor initialization/close helpers, standard unsupported/no-op cursor methods, and the opaque pointer verification for `WT_CURSOR_CONFIG`. It integrates with `WT_SESSION->open_cursor` dispatch for config cursor URIs.

## Risks
Risks are low. The main issues would be method table drift if config cursors later need traversal, incorrect key/value formats, or failing to close partially initialized cursors on open error.

## Test Signals
Signals include opening and closing config cursors, correct string key/value format exposure, unsupported-operation errors for traversal/mutation, no-op reset behavior, and leak checks for failed opens.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_ds.c -->
# sources/storage-engines/wiredtiger/src/cursor/cur_ds.c

## Purpose
This file implements WiredTiger wrapper cursors for extension-provided data sources. It translates WiredTiger cursor API calls to an underlying `WT_DATA_SOURCE` cursor while enforcing WiredTiger cursor state, statistics, collator comparison, and cleanup conventions.

## Important APIs, Types, and Functions
The public entry point is `__wt_curds_open`. Local operation wrappers include `__curds_key_set`, `__curds_value_set`, `__curds_cursor_resolve`, `__curds_bound`, `__curds_compare`, `__curds_next`, `__curds_prev`, `__curds_reset`, `__curds_search`, `__curds_search_near`, `__curds_insert`, `__curds_update`, `__curds_remove`, `__curds_reserve`, and `__curds_close`. Important types are `WT_CURSOR_DATA_SOURCE`, `WT_DATA_SOURCE`, `WT_CURSOR`, and optional `WT_COLLATOR`.

## Control Flow and Behavior
Open allocates a wrapper cursor, reads metadata for `key_format` and `value_format`, initializes the wrapper cursor, optionally configures a collator from metadata/app metadata, calls the extension `open_cursor`, and sanitizes the underlying cursor session, queue, recno, key/value, error, and flag fields.

For search/update style operations, wrappers copy the WiredTiger cursor key/value into the source cursor, call the source method, and resolve the result. For next/prev/search/search_near/insert/update/remove/reserve/bound, `__curds_cursor_resolve` copies successful source key/value/recno back into the wrapper, marks key/value internal, clears set flags on `WT_NOTFOUND`, clears internal flags on other errors, and resets the source cursor after failures to simplify extension behavior. Compare requires both cursors to reference the same object, compares recnos directly for record-number cursors, or uses the configured collator/default compare for byte-string keys. Close closes the source cursor, terminates owned collator, frees allocated formats, and closes the wrapper.

## State and Persistence
The wrapper keeps volatile cursor state and mirrors source cursor key/value/recno state. Persistent data is owned by the extension data source. The wrapper does not implement independent persistence.

## Dependencies and Integration Points
The file depends on metadata lookup, config parsing, collator configuration, cursor API/update/remove macros, system overload checks, statistics macros, extension `WT_DATA_SOURCE` methods, and standard cursor initialization/close helpers.

## Risks
Risks include extension cursors returning pointers with insufficient lifetime, source cursors retaining application memory after key/value assignment, wrapper/source flag divergence, reset-on-error side effects, collator ownership mistakes, and extensions not implementing methods assumed by the method table.

## Test Signals
Signals include extension data-source cursor CRUD behavior, custom collator comparison, append inserts, bound propagation, reset after errors, statistics increments, close cleanup with owned collator, unsupported modify behavior, and metadata-derived format correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/cursor/cur_ds.c -->
