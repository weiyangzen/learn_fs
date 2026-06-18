# Research: subset-b-009066

Grouped research for WiredTiger `test/format` and `test/fuzz` files. Each section is bounded for reconciliation into source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_prepare_discover.c -->
# sources/storage-engines/wiredtiger/test/format/format_prepare_discover.c

Purpose: implements `wts_prepare_discover`, a restart/open-time cleanup path for preserved prepared transactions when precise checkpoint and prepared-operation testing are both enabled. It opens a `prepared_discover:` cursor, claims each discovered prepared transaction by `claim_prepared_id=<id>`, then randomly resolves it as committed or rolled back.

Important APIs and functions: `WT_CONNECTION::open_session`, `WT_SESSION::open_cursor`, `WT_CURSOR::next/get_key/close`, `WT_SESSION::begin_transaction`, `timestamp_transaction_uint` for commit/durable/rollback timestamps, `commit_transaction`, `rollback_transaction`, `checkpoint`, `wts_verify_mirrors`, and format helpers such as `trace_msg`, `mmrand`, and `testutil_check`.

Control flow: the function returns immediately unless `GV(PRECISE_CHECKPOINT)` and `GV(OPS_PREPARE)` are set. It opens a session and discover cursor, treats `WT_NOTFOUND` from open as the normal no-work case, allocates a future timestamp via `g.timestamp += 10`, iterates all cursor entries, claims each prepared id, commits roughly half and rolls back the rest, checkpoints, then verifies mirrors against `WiredTigerCheckpoint` unless disaggregated storage disables checkpoint cursors.

State and persistence: it mutates `g.timestamp`, resolves prepared durable state that persisted across checkpoint/restart, and creates a checkpoint after resolution. The resolved prepared ids are removed from the prepared-discover stream by WiredTiger claim semantics. Mirror verification observes checkpoint state and disagg mode.

Dependencies and integration: called from `t.c` after open/create and `timestamp_init`. It depends on timestamp configuration, global RNG `g.extra_rnd`, tracing, and mirror verification from `verify.c`. It protects correctness for `preserve_prepared` and precise checkpoint configurations.

Risks and test signals: timestamp selection must remain greater than prepare timestamps; incorrect claim strings or timestamp ordering can panic prepared transaction resolution. `WT_NOTFOUND` is expected only for no cursor/open exhaustion. Useful signals are trace messages for discovered and claimed prepared ids, checkpoint success, and mirror verification failures after the resolution checkpoint.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_prepare_discover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_salvage.c -->
# sources/storage-engines/wiredtiger/test/format/format_salvage.c

Purpose: exercises WiredTiger salvage by first salvaging a valid object, then corrupting a backing file and salvaging again. It is a post-run fault-tolerance path for table/file sources.

Important APIs and functions: `uri_path` maps `table->uri` to an object file path under `g.home`; `corrupt` writes a repeatable corruption marker into a random file span and saves `SALVAGE.corrupt` plus `SALVAGE.copy/<object>.corrupted`; `wts_salvage` drives open, `WT_SESSION::salvage(force=true)`, `table_verify`, and close cycles.

Control flow: `wts_salvage` exits when `GV(OPS_SALVAGE)` is off, creates `SALVAGE.copy`, copies the target object and WiredTiger metadata/log files, opens the database with metadata verification, salvages and verifies, closes, corrupts the object, reopens without metadata verification, salvages again, verifies again, and closes.

State and persistence: it modifies real files in `g.home`, writes diagnostic salvage artifacts, and preserves enough copied state to replay failures. Corruption is roughly 2 percent of file size plus 4 KiB, capped at 1 MiB, and starts at a random offset before the final KiB.

Dependencies and integration: called from `t.c` after normal verification and shutdown, per table via `tables_apply`. It uses `wts_open/wts_close`, `table_verify`, `testutil_copy`, POSIX file APIs, global RNG, and path fields from `GLOBAL`.

Risks and test signals: small files below the assumed offset range would be risky if salvage were enabled for unsuitable objects. The important failures are inability to locate the object, failed salvage, failed verify, or mismatch introduced by salvage. `SALVAGE.corrupt` records the corruption offset/length for reproduction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_salvage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_timestamp.c -->
# sources/storage-engines/wiredtiger/test/format/format_timestamp.c

Purpose: centralizes format's timestamp lifecycle: initialize from recovery, periodically advance oldest/stable timestamps, compute safe committed bounds, and do final timestamp advancement before verification.

Important APIs and functions: `timestamp_query`, `timestamp_init`, `timestamp_minimum_committed`, `timestamp_sync_threads_commit_ts`, `timestamp_once`, `timestamp` thread, and `timestamp_teardown`. WiredTiger APIs include `WT_CONNECTION::query_timestamp` and `set_timestamp`.

Control flow: initialization queries `get=recovery` and falls back to `MIN_TIMESTAMP`. `timestamp_minimum_committed` returns one less than the minimum in-use thread commit timestamp, or delegates to predictable replay's `replay_maximum_committed`. `timestamp_once` computes oldest/stable, applies replay stop/lags rules, sets both timestamps under `g.prepare_commit_lock`, updates `g.oldest_timestamp` and `g.stable_timestamp`, and optionally traces. The timestamp thread sleeps at normal or replay-specific cadence until `g.workers_finished`.

State and persistence: owns `g.timestamp`, `g.oldest_timestamp`, `g.stable_timestamp`, and per-thread `TINFO.commit_ts` synchronization. It persists timestamp state through WiredTiger connection-level `set_timestamp`, impacting visibility, checkpoint stability, rollback-to-stable, and verification.

Dependencies and integration: used by `t.c`, `ops.c`, `replay.c`, `snap.c`, and `wts.c` precise checkpoint setup. It depends on `tinfo_list`, `g.prepare_commit_lock`, replay mode, and timestamped table configuration.

Risks and test signals: stale or unset thread commit timestamps intentionally block advancement; bad advancement can make prepared commits panic or age out snapshot verification. Signals include trace `set ts`, query failures, RTS behavior, and final verify failures caused by oldest/stable not advancing far enough.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_util.c -->
# sources/storage-engines/wiredtiger/test/format/format_util.c

Purpose: supplies common runtime utilities for progress display, path setup, lock abstraction, diagnostic page dumps, numeric parsing, wrapped session lifecycle, and session prefetch selection.

Important APIs and functions: `track_ops`, `track`, `path_setup`, `fclose_and_clear`, `lock_init`, `lock_destroy`, `cursor_dump_page`, `table_dump_page`, `set_core`, `atou32`, `wt_wrap_open_session`, `wt_wrap_close_session`, and `session_prefetch_cfg`.

Control flow: progress helpers render single-line operation counts and timestamp movement unless `GV(QUIET)` is set. Path setup fills `g.home*` paths. Lock helpers choose WiredTiger rwlocks or pthread rwlocks from config. Page dump helpers open a cursor, position by table type, and, in diagnostic builds, catch dump crashes via `sigsetjmp` around `__wt_debug_cursor_page`. Session wrappers attach `SAP` app-private tracking and trace sessions.

State and persistence: updates process-visible stdout progress, global path fields, `RWLOCK.lock_type`, trace session handles in `SAP`, and diagnostic `FAIL.pagedump.N` files. `set_core` mutates process rlimit state around unsafe dumps or expected failures.

Dependencies and integration: used broadly by `t.c`, `ops.c`, `verify.c`, `wts.c`, salvage, import, random cursor, and timestamp threads. It depends on `format.h`, WiredTiger internals, POSIX signals/rlimits, and test utility allocation/error helpers.

Risks and test signals: `track_write` assumes single-threaded callers. Diagnostic dump handlers are best-effort and only compiled under `HAVE_DIAGNOSTIC`. Wrapping sessions correctly is essential because trace routing and progress tags depend on `session->app_private`; leaks or stale app-private state can corrupt trace teardown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/format_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/hs.c -->
# sources/storage-engines/wiredtiger/test/format/hs.c

Purpose: optional background thread that scans WiredTiger history store cursors to exercise internal ordering checks while the workload mutates data.

Important APIs and functions: `hs_cursor`, `__wt_curhs_next_hs_id`, `__wt_curhs_open_ext`, cursor `next/prev/get_key/get_value/close`, and session wrapper/prefetch helpers. It is disabled at compile time for WiredTiger major versions below 10.

Control flow: opens one session, loops until `g.workers_finished`, enumerates history store ids, opens each HS cursor, sets read-committed cursor flags, chooses forward or reverse traversal, performs 1,000 to 100,000 steps, tolerates `WT_NOTFOUND`, `WT_CACHE_FULL`, and `WT_ROLLBACK`, closes the cursor, then sleeps 1 to 10 seconds in short intervals.

State and persistence: it does not intentionally mutate user data, but it reads internal history store records and can pin/cache pages transiently. It stores decoded key/value components only in local variables.

Dependencies and integration: spawned from `operations` when `GV(OPS_HS_CURSOR)` is enabled. It relies on WiredTiger internal history-store cursor APIs, `g.wts_conn`, `g.extra_rnd`, and `session_prefetch_cfg`.

Risks and test signals: because this intentionally uses internal APIs and cursor flags, version drift is a risk. Expected transient returns are cache/rollback/notfound; any other cursor error is a failure signal. It can reveal ordering bugs through WiredTiger diagnostic assertions rather than application-level comparisons.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/hs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/import.c -->
# sources/storage-engines/wiredtiger/test/format/import.c

Purpose: runs a background import workload that repeatedly imports a simple table file from a secondary database into the main format home, validating import metadata, repair, dry-run-like alter/drop/reimport, and fallback repair behavior.

Important APIs and functions: `import`, `populate_table`, `verify_import`, `get_file_metadata`, and `copy_file_into_directory`. WiredTiger APIs include `create`, `checkpoint`, `alter`, metadata cursor reads, `drop(remove_files=false)`, `open_cursor`, and internal `__wt_copy_and_sync`.

Control flow: creates `g.home/IMPORT`, opens a separate connection, creates and populates `table:import` with 1,000 integer key/value pairs, captures table and file metadata, then until workers finish copies `import.wt` to the parent home and chooses one of several import modes: repair-only, metadata import, or import/checkpoint/alter/checkpoint/drop-keep-file/reimport with possible repair fallback. Every import is verified and dropped before sleeping.

State and persistence: creates a secondary WiredTiger database and repeatedly copies/imports `import.wt` into the main home. It depends on persistent metadata strings for `table:import` and `file:import.wt`, and intentionally leaves the source import database stable across iterations.

Dependencies and integration: spawned by `operations` when `GV(IMPORT)` is set. It uses `create_database` from `wts.c`, main `g.wts_conn`, testutil drop helpers, and global extra RNG. It runs concurrently with other workload threads.

Risks and test signals: metadata strings must remain valid after retrieval; forced checkpoints can make non-repair reimport fail, which is expected only before fallback. Verification asserts every key/value equals its ordinal and exactly 1,000 entries exist; failures identify import corruption, metadata mismatch, or copy/sync bugs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/import.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/kv.c -->
# sources/storage-engines/wiredtiger/test/format/kv.c

Purpose: defines deterministic key and value generation for format tables, including persisted random key length tables for reopen compatibility and value patterns that support verification, prefix compression, overflow, and RLE testing.

Important APIs and functions: `key_init`, `key_gen_init`, `key_gen_teardown`, `key_gen_common`, `val_init`, `val_gen_init`, `val_gen_teardown`, and `val_gen`; static helpers `key_init_random` and `val_len`.

Control flow: row-store tables get a `key_rand_len` table generated or reloaded from `CONFIG.keylen[.<table id>]`. Key buffers are initialized with alphabetic filler, optional common prefixes are generated from key-number buckets, and keys encode a zero-padded number plus suffix. Values use recognizable base data, zero-length values every 63rd key, duplicate value patterns for variable-column-store RLE, and occasional 80-100 KiB overflow-sized items.

State and persistence: persists key length choices to `g.home_key` so reopened runs regenerate identical row-store keys. It owns `TABLE.val_base`, `TABLE.val_dup_data_len`, and `TABLE.key_rand_len`. Generated data embeds key numbers for readable trace and verification.

Dependencies and integration: used by bulk load, ops, verify, snapshot replay, salvage diagnostics, and table creation. It depends on config macros (`TV`, `table_maxv`), global RNG, table type, and prefix length global `g.prefix_len_max`.

Risks and test signals: key format assumptions are shared with mirror verification and original-row filtering; changing suffix layout or minimum length can break parsing. Buffer sizing must account for largest configured keys/values plus prefixes. Reopen correctness depends on reading the exact saved length file.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/kv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/ops.c -->
# sources/storage-engines/wiredtiger/test/format/ops.c

Purpose: the main concurrent workload engine for format. It creates worker `TINFO` structures, starts worker and auxiliary threads, selects operations, manages transactions/timestamps/prepared transactions, performs cursor operations, handles rollback/retry, and drives rollback-to-stable verification.

Important APIs and functions: orchestration functions `operations`, `ops`, `tinfo_init`, `tinfo_teardown`, `rollback_to_stable`; transaction helpers `begin_transaction_ts`, `begin_transaction`, `commit_transaction`, `rollback_transaction`, `prepare_transaction`; operation executor `table_op`; row/column operations for read, next/prev, reserve, modify, truncate, update, insert, remove; column insert drain helpers; cursor bound helpers; and `wts_read_scan`.

Control flow: `operations` computes stop criteria, opens a control session, initializes lanes/thread info, starts worker threads plus optional alter/background compact/backup/compact/follower/history-store/import/random/timestamp/checkpoint threads, polls operation totals, signals quit, joins all threads, runs rollback-to-stable, disagg sync, replay cleanup, final timestamp teardown, and session close. Each worker repeatedly opens/resets sessions, selects tables and operations by config, begins timestamped or non-timestamped transactions, performs mirrored operations across tables when required, verifies snapshot repeatability, optionally prepares, commits or rolls back, retries predictable replay rollbacks with the same timestamp, and resolves column-store appended row counts.

State and persistence: mutates all major workload state: `tinfo_list`, per-thread cursors/counters/RNGs/snapshot lists, `g.lanes`, `g.workers_finished`, `g.stop_timestamp`, `g.truncate_cnt`, `g.timestamp`, and `TABLE.rows_current`. Persistent effects are WiredTiger updates/inserts/removes/modifies/truncates, checkpoints from auxiliary threads, rollback-to-stable state, and optional recovery-abort crashes.

Dependencies and integration: integrates nearly every format module: timestamp, replay, snap, kv, wts, verify, random, import, hs, checkpoint/backup/alter/compact/follower modules, table selection/cursor wrappers from `format_inline.h`, and global config from `format_config`. It uses WiredTiger cursor/session/connection APIs extensively.

Risks and test signals: this file encodes many invariants: predictable replay allows only one operation per transaction, lane-derived keys must avoid concurrent same-key writes, truncates are gated by `g.truncate_cnt`, prepared commit timestamps are protected by `g.prepare_commit_lock`, and snapshot repeat checks must distinguish rollback/cache-full/notfound. Strong signals include assertion failures, unexpected operation return codes, 15-minute post-timeout aborts with debug info, mirrored truncate mismatches, RTS repeat failures, and trace entries around transaction boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/random.c -->
# sources/storage-engines/wiredtiger/test/format/random.c

Purpose: optional background smoke test for random cursors on row-store tables.

Important APIs and functions: `random_kv`, `table_select_type`, `wt_wrap_open_session`, `wt_wrap_open_cursor`, random cursor config `next_random=true` and `next_random_sample_size=37`, cursor `next/get_key/get_value/close`.

Control flow: exits if no row-store table exists. It opens a session, alternates between simple and sample-size random cursor configurations, selects a row-store table, performs up to 1,000 `next` calls, tolerates normal transient returns, reads returned key/value pairs, closes the cursor, sleeps 1 to 10 seconds, and repeats until `g.workers_finished`.

State and persistence: read-only except transient cursor/session state and cache effects. It samples live data while concurrent writes continue.

Dependencies and integration: spawned by `operations` under `GV(OPS_RANDOM_CURSOR)`. It depends on row-store table metadata, global extra RNG, and session prefetch wrapper behavior.

Risks and test signals: it intentionally does not validate key distribution, only API stability. Unexpected cursor errors are the main failure signal. It is skipped for pure column-store workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/replay.c -->
# sources/storage-engines/wiredtiger/test/format/replay.c

Purpose: implements predictable replay, where operations at a given timestamp are deterministic across runs with the same seeds and data can be compared at matching stable timestamps.

Important APIs and functions: `replay_end_timed_run`, `replay_maximum_committed`, `replay_operation_enabled`, `replay_loop_begin`, `replay_run_begin`, `replay_run_end`, `replay_read_ts`, `replay_prepare_ts`, `replay_commit_ts`, `replay_rollback_ts`, `replay_committed`, `replay_adjust_key`, `replay_rollback`, `replay_stale_read_ts`, and `replay_pause_after_rollback`. Static `replay_pick_timestamp` and `replay_run_reset` manage lane allocation.

Control flow: each replay operation claims a unique timestamp, maps its low bits to a lane, marks the lane in use, seeds per-thread data/extra RNGs from timestamp xor configured seeds, and constrains keys to the same lane. Commits update lane `last_commit_ts`; if global timestamp has advanced more than one lane cycle, the same thread must replay the next timestamp in that lane. Rollbacks retain timestamp/lane and retry. Stable timestamp computation scans in-use lanes and caches the largest safe committed timestamp.

State and persistence: controls `g.timestamp`, `g.timestamp_copy`, `g.stop_timestamp`, `g.replay_start_timestamp`, `g.replay_cached_committed`, `g.replay_calculate_committed`, `g.lanes[]`, and per-thread replay fields. It indirectly determines all persisted data values by seeding RNGs and selecting keys/operations.

Dependencies and integration: used by `ops.c` transaction and key-selection paths, `format_timestamp.c` timestamp advancement, and snapshot retry handling. It requires timestamped transactions and forbids truncate operations in replay mode.

Risks and test signals: any non-replay mutation of `g.timestamp` violates `timestamp_copy` assertions. Lane release/reclaim bugs can permit same-key races or make stable timestamp move incorrectly. Signals include deterministic compare failures, replay assertions, stuck rollback retries, and stale read timestamp detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/replay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/smoke.sh -->
# sources/storage-engines/wiredtiger/test/format/smoke.sh

Purpose: make-check smoke wrapper for the format binary.

Important commands and parameters: builds a common `args` string with `-c .`, compression/logging compression off, `cache.minimum=40`, `runs.rows=100000`, table source, three tables, six threads, one-minute timer, and transaction timestamps enabled; runs `$TEST_WRAPPER ./t ... runs.type=row` and then `runs.type=var`.

Control flow: `set -e` fails on any command error. The script performs two short format runs, one row-store and one variable column-store.

State and persistence: creates whatever `./t` creates in its default `RUNDIR` unless wrapper/config overrides. It does not clean by itself.

Dependencies and integration: used by build/test harness, depends on `TEST_WRAPPER`, local format binary `./t`, and generated format configuration parser.

Risks and test signals: because `set -e` is active, non-zero format exit fails smoke. It provides quick coverage for timestamped multi-table row and var workloads but not the full option surface.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/snap.c -->
# sources/storage-engines/wiredtiger/test/format/snap.c

Purpose: tracks recent operations per worker so format can repeat reads/updates under snapshot isolation and validate rollback-to-stable visibility.

Important APIs and functions: `snap_init`, `snap_teardown`, `snap_op_init`, `snap_track`, `snap_repeat_txn`, `snap_repeat_update`, `snap_repeat_single`, and `snap_repeat_stable`. Static helpers decide repeatability, perform cursor verification, clear aged-out timestamps, and compare overlapping operations/truncates.

Control flow: each thread maintains circular `SNAP_OPS` buffers, two buffers when timestamps are enabled. At transaction start `snap_op_init` records read/stable timestamp context and swaps buffers when stable advances. `snap_track` saves operation type, table id, key number, row insert key, value, truncate range, and op id. Before commit, `snap_repeat_txn` verifies repeatable operations in the unresolved transaction. After commit/rollback, `snap_repeat_update` marks operations repeatable at read or commit timestamp. Later single/stable repeat paths begin read-timestamp transactions and re-read saved keys.

State and persistence: stores copies of keys/values in per-thread memory and uses timestamps to read historical persisted state. It clears entries after stable RTS verification or when timestamps age out.

Dependencies and integration: called from `ops.c` around transaction begin, operation execution, transaction resolution, and RTS. It uses `table_cursor`, key generation, `read_op`, trace macros, page dumps, and WiredTiger internal callback hooks on `WT_SESSION_IMPL::format_private`.

Risks and test signals: circular buffer wrap disables repeat checks for that transaction. Truncates are hard to repeat and mostly excluded. Snapshot mismatch prints expected/found data, dumps pages, and asserts; excessive rollback during repeat is tolerated only for oldest-for-eviction cases with a warning.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/snap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/t.c -->
# sources/storage-engines/wiredtiger/test/format/t.c

Purpose: main entry point for the format test program. It parses command-line/config input, initializes global process state, creates or reopens the database, drives load/verify/read-scan/operation phases, and handles shutdown, salvage, tracing, and failure reporting.

Important APIs and functions: `main`, `format_process_env`, `set_alarm`, `locks_init`, `locks_destroy`, `format_die`, and `usage`. It coordinates `config_*`, `path_setup`, `disagg_setup/teardown`, `wts_*`, `timestamp_*`, `tables_apply`, `operations`, `trace_*`, and `wts_salvage`.

Control flow: process setup installs signal handlers and RNGs, parses options `-B -C -c -h -q -R -S -T -v`, loads config, configures RNGs and disaggregated processes, runs `config_run`, creates/reopens WiredTiger, initializes timestamps, discovers prepared transactions, initializes key/value data, bulk-loads when new, verifies, optionally read-scans, starts checkpointing, runs three operation phases or disagg leader/follower switch phases, dumps stats, verifies again, closes, salvages, tears down tracing/disagg, prints success, and clears config.

State and persistence: defines global `GLOBAL g`, `TABLE *tables[]`, and `ntables`. It owns home paths, reopen behavior, process-level locks, signal timers, and database lifecycle. It writes `CONFIG`, stats, trace dirs, database files, and possible salvage artifacts through called modules.

Dependencies and integration: top-level integration point for all format modules and the test utility library. It also depends on WiredTiger version macros for backward compatibility and on external harness behavior that scans output strings.

Risks and test signals: some output strings are harness contracts, notably process running, alarm timeout, abort-to-test-recovery, run FAILED, and successful completion. Error handling intentionally serializes on `g.death_lock`, disables trace/progress, prints config, and sleeps before teardown to expose failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/trace.c -->
# sources/storage-engines/wiredtiger/test/format/trace.c

Purpose: configures and owns an auxiliary WiredTiger log database used for operation/message tracing.

Important APIs and functions: `trace_config`, `trace_init`, and `trace_teardown`. It recognizes trace options `all`, `bulk`, `cursor`, `mirror_fail`, `read`, `timestamp`, `txn`, and `retain=<n>`.

Control flow: `trace_config` duplicates the config string, marks recognized tokens as consumed, sets flags and retention, rejects leftover non-comma/non-space characters, then enables tracing. `trace_init` creates `g.home/OPS.TRACE`, opens a logging-enabled WiredTiger connection with log removal and retention, opens a global session, and initializes a spinlock. `trace_teardown` nulls `g.trace_conn`, destroys the lock, and closes the trace connection.

State and persistence: mutates `g.trace_flags`, `g.trace_retain`, `g.trace_conn`, `g.trace_session`, and `g.trace_lock`. Persists trace logs under `OPS.TRACE` with retained log files and statistics logs.

Dependencies and integration: selected by `t.c -T`; used by trace macros in `format_inline.h`, event handling in `wts.c`, and session wrappers in `format_util.c`.

Risks and test signals: config parsing is substring-based and consumes recognized words in a copy, so option names must remain unambiguous. Teardown must tolerate being called during failure and normal shutdown. Trace retention defaults to at least 10 files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/verify.c -->
# sources/storage-engines/wiredtiger/test/format/verify.c

Purpose: verifies table integrity with WiredTiger verify and checks mirrored tables contain equivalent original key/value data, including live, checkpoint, and mirrored-truncate-specific ranges.

Important APIs and functions: `table_verify`, `wts_verify`, `wts_verify_mirrors`, `wts_verify_mirrored_truncate`, and static mirror helpers `table_mirror_row_next`, `position_cursor_before`, `table_verify_mirror`, and failure reporting/page dump functions.

Control flow: `wts_verify` checkpoints, applies strict verify to each table, then optionally verifies mirrors unless salvage/reopen makes mirror comparison invalid. `table_verify_mirror` opens base and target cursors, retries checkpoint cursor open until checkpoint ids match, pins a live snapshot when not using checkpoint cursors, positions to a requested range for truncate checks, walks original records, compares key numbers and values, dumps diagnostic pages on first mismatch, and asserts no failures.

State and persistence: mostly read-only but creates checkpoints before verify and diagnostic page dumps on mismatch. It uses live snapshots or named checkpoint state and may preserve disaggregated layered components on first mismatch.

Dependencies and integration: invoked by `t.c`, `format_prepare_discover.c`, salvage, and `ops.c` mirrored truncates. It depends on `key_gen`, `atou32`, cursor wrappers, table metadata, trace flags, disagg settings, and WiredTiger strict verify.

Risks and test signals: mirror checks intentionally skip row-store inserted non-original keys and stop when both sides pass original rows. Live verification requires a pinned cursor to avoid snapshot refresh. Signals include strict verify errors, EBUSY warnings after retry, mirror mismatch messages, `FAIL.pagedump` diagnostics, and disagg preservation artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/wts.c -->
# sources/storage-engines/wiredtiger/test/format/wts.c

Purpose: builds WiredTiger connection/table configuration for format, opens/closes databases, creates objects, handles event messages/progress, reopens connections, initializes precise checkpoint support, and writes statistics.

Important APIs and functions: `create_database`, `create_object`, `wts_create_home`, `wts_create_database`, `wts_open`, `wts_close`, `wts_reopen`, `wts_stats`, plus configuration helpers for encryption, timing stress, file manager, debug mode, eviction, live restore, disaggregated storage, tiered storage, prefetch, and obsolete cleanup.

Control flow: configuration helpers append settings into bounded buffers based on global/table config. `create_database` constructs a `wiredtiger_open` config with cache, statistics, in-memory/logging/encryption/block cache/checkpoint/timing/debug/disagg/tiered/prefetch/extensions/user overrides, then opens the connection. `create_object` builds per-table `WT_SESSION::create` config for key format, page sizes, compression, prefix compression, checksums, timestamps/logging, layered/disagg, and assertions. Open/close paths add nonpersistent options and optional metadata verification; stats opens statistics cursors and writes connection plus per-data-source stats.

State and persistence: creates/removes home directories, creates database/table files, updates `g.wts_conn` and `g.wts_conn_inmemory`, writes `OPERATIONS.stats`, opens extension libraries, and persists WiredTiger metadata/configuration. Precise checkpoint init sets stable timestamp before close after initial create.

Dependencies and integration: called by `t.c`, import, salvage, and reopen paths. It depends on `format_config`, `test_util` storage helpers, extension paths, event handler callbacks, trace connection state, disagg/tiered testutil builders, and global encryption keys.

Risks and test signals: config buffer exhaustion is fatal. Backward compatibility changes close behavior. In-memory mode uses one shared handle. Event handler routes verbose messages to trace or stdout and Antithesis-prefixed messages to stdout. Open failures include the generated home/config in diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/wts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/fuzz/CMakeLists.txt

Purpose: CMake build/test definition for WiredTiger libFuzzer targets.

Important APIs and functions: `check_c_source_compiles` detects clang libFuzzer support; `add_library(fuzz_util SHARED fuzz_util.c)` builds the fuzz utility library; `create_test_executable` builds `test_fuzz_modify` and `test_fuzz_config`; `add_test` runs each target through `fuzz_run.sh`.

Control flow: it temporarily sets CMake required flags/libraries for fuzzer detection, returns early if libFuzzer is missing, selects `wiredtiger_static` when static+PIC is enabled or `wiredtiger_shared` when shared is enabled, returns early otherwise, builds `fuzz_util` with include paths and sanitizer flags, then defines and registers fuzz executables.

State and persistence: affects build graph only. It copies `fuzz_run.sh` as an additional file for each target and links sanitizer runtime into fuzz targets.

Dependencies and integration: depends on CMake helper macros from the WiredTiger build, `test_util`, configured include directories, clang `-fsanitize=fuzzer`, and either shared or PIC static WiredTiger library.

Risks and test signals: targets silently skip when prerequisites are unavailable, with a status message for library shape but not for missing fuzzer. Link/compile failures usually indicate sanitizer/toolchain mismatch or missing PIC/shared library support.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/config/fuzz_config.c -->
# sources/storage-engines/wiredtiger/test/fuzz/config/fuzz_config.c

Purpose: libFuzzer target for WiredTiger configuration parser lookups.

Important APIs and functions: `LLVMFuzzerTestOneInput`, `fuzzutil_setup`, `fuzzutil_sliced_input_init`, `fuzzutil_slice_to_cstring`, `__wt_config_getones`, and `fuzzutil_sliced_input_free`.

Control flow: initializes fuzz utility state, splits input into exactly two slices separated by `|`, converts slice 0 to a null-terminated key and slice 1 to a null-terminated config string, calls `__wt_config_getones` with `fuzz_state.session`, ignores the result value, frees all temporary inputs, and returns 0. Inputs without two slices are ignored.

State and persistence: creates heap strings for fuzzer data and uses shared fuzz utility session state. It does not persist files directly.

Dependencies and integration: built by `test/fuzz/CMakeLists.txt` and run by `fuzz_run.sh`. It depends on `fuzz_util.h`, WiredTiger internal config parser APIs, and the fuzzer runtime entrypoint contract.

Risks and test signals: the delimiter split means fuzz coverage focuses on key/config combinations, not arbitrary binary config alone. Crashes, assertion failures, sanitizer reports, leaks, or timeouts are meaningful parser robustness signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/config/fuzz_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/fuzz_coverage.sh -->
# sources/storage-engines/wiredtiger/test/fuzz/fuzz_coverage.sh

Purpose: post-processes clang fuzzing coverage data into text and HTML reports for a fuzz target.

Important commands and variables: accepts `<fuzz-test-binary>`, uses `PROFDATA_BINARY` or `llvm-profdata`, uses `COV_BINARY` or `llvm-cov`, merges `*.profraw` into `<binary>_cov.profdata`, and writes `<binary>_cov.txt` plus `<binary>_cov.html`.

Control flow: validates an argument, resolves tool binaries with defaults and informational messages, removes previous coverage outputs, checks for `.profraw` files, exits with guidance if none exist, runs `llvm-profdata merge -sparse`, then runs `llvm-cov show` twice for text and HTML output.

State and persistence: deletes previous `*_cov.profdata`, `*_cov.txt`, and `*_cov.html` in the current directory, reads all `.profraw`, and writes new coverage artifacts next to the run outputs.

Dependencies and integration: intended after `fuzz_run.sh` in a build configured with `-fprofile-instr-generate` and `-fcoverage-mapping`. Requires clang coverage tools compatible with the compiler output.

Risks and test signals: wildcard cleanup is scoped only by current directory naming, so callers must run it in the fuzz output directory. Missing `.profraw` or tool command failures produce non-zero exits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/fuzz_coverage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/fuzz_run.sh -->
# sources/storage-engines/wiredtiger/test/fuzz/fuzz_run.sh

Purpose: standard runner for WiredTiger libFuzzer binaries.

Important commands and variables: accepts `<fuzz-test-binary> [fuzz-test-args]`, removes previous `WT_TEST_*`, `.profraw`, and `fuzz-*.log` outputs, exports `LLVM_PROFILE_FILE=WT_TEST_%p.profraw`, and executes the fuzzer with `-jobs=8 -runs=100000000 -close_fd_mask=3`.

Control flow: validates an argument, stores and shifts the binary path so extra args pass through to the fuzzer, cleans prior run artifacts, sets coverage profile naming, then starts libFuzzer with parallel workers, a finite large run count, suppressed stdout/stderr, and any caller-provided corpus/options.

State and persistence: creates `WT_TEST_<pid>` homes, per-worker profiler files, libFuzzer logs, and crash artifacts in the current directory. It removes old matching artifacts before each run.

Dependencies and integration: used by CTest entries in `test/fuzz/CMakeLists.txt`. It assumes the target is a libFuzzer binary and benefits from ASan/coverage builds.

Risks and test signals: `-close_fd_mask=3` prevents log spam but hides target output during the run; reproducing crashes without the mask may be needed. Large run count can be expensive, and cleanup wildcards require a dedicated working directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/fuzz_run.sh -->
