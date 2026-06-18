# subset-b-009059 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/schema_abort/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/schema_abort/main.c

Purpose: this C test is a crash-recovery stress harness for WiredTiger schema operations running concurrently with timestamped and non-timestamped writes. It creates three verification tables that model MongoDB-style usage: a logged local table, a logged timestamped oplog table, and a non-logged timestamped collection table. Most worker threads also perform random schema operations against a separate `table:wt` object, then the parent process kills the child after checkpoint readiness and verifies that recovery preserves the expected data visibility.

Important APIs, types, and functions: the file is built on `test_util.h`, `WT_CONNECTION`, `WT_SESSION`, `WT_CURSOR`, `WT_EVENT_HANDLER`, `WT_LAZY_FS`, `wt_thread_t`, and WiredTiger timestamp APIs. `THREAD_DATA` carries connection, key-space start, thread id, and random states. `THREAD_TS` records the latest committed timestamp and current schema operation for diagnostics. Schema exercisers include `test_bulk`, `test_bulk_unique`, `test_cursor`, `test_create`, `test_create_unique`, `test_drop`, and `test_verify`. Runtime threads are `thread_run`, `thread_ckpt_run`, and `thread_ts_run`; the parent-side verifier is in `main`.

Control flow: `main` parses options, chooses random or explicit thread count and timeout, creates `WT_TEST` subdirectories, optionally initializes LazyFS, then forks. The child `run_workload` opens WiredTiger with logging/statistics and optional aggressive sweep or fsync transaction sync, creates the collection/local/oplog tables, starts checkpoint and timestamp threads, and starts writer threads. Writers reserve deterministic timestamps with `RESERVED_TIMESTAMP_FOR_ITERATION`, write records to all three tables, record `(stable_ts,key)` in per-thread files, and interleave schema operations. The checkpoint thread repeatedly checkpoints with `use_timestamp=true`, optionally does tiered flushes, and creates `child_ready` once the kill condition is safe. The parent waits for that sentinel, kills the child, opens the database to force recovery, and verifies all recorded keys.

State and persistence behavior: the durable state under test is a mix of WiredTiger data files, logs, checkpoints, metadata/schema changes, sidecar `records-N` files, and the checkpoint readiness file. Timestamp state advances only when all writer threads have committed past a point; oldest and stable timestamps are moved together. Verification uses `query_timestamp(get=recovery)` and expects collection data only at or below the recovery stable timestamp, while local and oplog tables should contain all logged data except in-memory log buffering edge cases. LazyFS mode deliberately clears cache after saving debug copies to simulate storage loss.

Dependencies and integration points: the test depends on WiredTiger internal test helpers for work directories, random seeds, tiered storage, LazyFS, process waiting, and cleanup. Smoke scripts invoke it as `test_schema_abort` across row/column, in-memory, compatibility, timestamp-off, transaction, and sweep variants. It also integrates with tiered storage helpers through `testutil_tiered_begin`, `testutil_tiered_sleep`, and `testutil_tiered_flush_complete`.

Risks and test signals: this test intentionally accepts races such as `ENOENT`, `EBUSY`, and some `EINVAL` outcomes around concurrent schema operations. High-risk areas are timestamp advancement, partial records in sidecar files, expected missing suffixes versus fatal holes, and option interactions such as transactions with bulk load or tiered drops. Passing signal is a recovery open followed by record verification and cleanup. Failures print missing ranges per table, child abnormal exits, stable timestamp startup timeout, or unexpected WiredTiger API errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/schema_abort/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/schema_abort/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/schema_abort/smoke.sh

Purpose: this shell wrapper runs a bounded smoke matrix for `test_schema_abort` as part of `make check`. It gives the heavyweight crash-recovery schema abort test short, deterministic coverage by forcing `-t 10 -T 5` rather than letting the C test choose random timeout and thread counts.

Important APIs and variables: it uses POSIX `sh`, `set -e`, optional positional argument `$1` for a manually supplied binary path, `binary_dir` fallback, and `TEST_WRAPPER` to integrate with the build/test harness. The default binary is `$binary_dir/test_schema_abort`.

Control flow: the script resolves the executable, then runs eighteen invocations. The first group covers default row-store timestamped runs, in-memory mode, compatibility mode, aggressive sweep in compatibility mode, and in-memory plus compatibility. The second group repeats those combinations with `-c` for variable-length column-store. The third group disables timestamps with `-z` across default, sweep, in-memory, and in-memory column-store. The final group enables transactional schema operations with `-x` across default, sweep, in-memory, and in-memory column-store.

State and persistence behavior: the script itself persists no state. Each child test creates and normally removes its own WiredTiger home unless configured otherwise through inherited wrapper/test options.

Dependencies and integration points: it assumes the build system either passes the binary as `$1` or syncs the smoke script next to `test_schema_abort`. `TEST_WRAPPER` may inject sanitizer, timeout, or environment handling.

Risks and test signals: `set -e` makes the first failing variant fail the smoke script. Coverage is intentionally broad but shallow; it does not cover LazyFS or tiered storage, which have separate wrappers or build configurations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/schema_abort/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/schema_abort/smoke_lazyfs.sh -->
# sources/storage-engines/wiredtiger/test/csuite/schema_abort/smoke_lazyfs.sh

Purpose: this smoke wrapper runs the schema abort crash-recovery harness with LazyFS enabled. LazyFS coverage is separated from the main smoke matrix because the storage-cache clearing behavior requires a longer timeout and different environmental assumptions.

Important APIs and variables: it uses POSIX `sh`, `set -e`, an optional first argument for the test binary, `binary_dir` fallback, and `TEST_WRAPPER`. The resolved binary defaults to `test_schema_abort`.

Control flow: after resolving the binary, it executes two runs: `-l -t 20 -T 5` and `-l -C -t 20 -T 5`. Both enable LazyFS explicitly, use five worker threads, and allow twenty seconds. The second run adds compatibility mode.

State and persistence behavior: persistent state is created by the underlying C test. LazyFS causes the child/parent flow to simulate filesystem cache loss and cleanup via `testutil_lazyfs_setup`, `testutil_lazyfs_clear_cache`, and `testutil_lazyfs_cleanup`.

Dependencies and integration points: the script depends on a build where LazyFS support is available or implicitly configured. It relies on `TEST_WRAPPER` for environment handling and on the same binary-location convention as the main schema abort smoke test.

Risks and test signals: the smoke signal is binary exit status. The matrix is small, so it checks LazyFS plus compatibility only, not the full row/column/timestamp/transaction cross product.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/schema_abort/smoke_lazyfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/scope/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/scope/main.c

Purpose: this test verifies WiredTiger cursor key/value scope rules. It checks when an application may overwrite buffers after cursor operations and whether `get_key` and `get_value` return copied library-owned data or correct errors after insert, modify, search, search-near, reserve, update, and remove variants.

Important APIs, types, and functions: it uses `WT_EVENT_HANDLER` to suppress expected "requires key/value be set" messages, `WT_CURSOR`, `WT_SESSION`, `WT_MODIFY`, `WT_ITEM`, and helper macros `SET_KEY` and `SET_VALUE`. `cursor_scope_ops` is the main behavioral matrix. `run` creates a data source and applies the matrix. `main` opens WiredTiger and runs the matrix for file and table URIs with string keys, recno keys, string values, and raw byte values.

Control flow: each operation case creates a clean key/value record if needed, begins a snapshot transaction, opens a fresh cursor, sets application key/value buffers, performs the operation, overwrites the original buffers with marker bytes, then probes cursor state. Insert and key-based remove are expected not to position the cursor; positioned remove should preserve the key but not value; modify, reserve, search, search-near, and update should preserve both key and value through library-owned memory. Operations that intentionally create cursor state errors roll back the transaction; others commit.

State and persistence behavior: the database is temporary and created under `opts->home`. There is no crash or recovery phase. The persistent state is only the records created and removed in each data source; the real focus is transient cursor state and memory ownership after API calls.

Dependencies and integration points: this is a standalone csuite test using common `testutil_parse_opts`, `testutil_recreate_dir`, and `testutil_cleanup`. It exercises both `file:` and `table:` data sources and both row-store and column-store key formats.

Risks and test signals: the most important risk is accidental retention of application memory pointers after operations, which could become use-after-modify bugs in callers. Passing requires all `testutil_assert` checks and expected error filtering to complete. Any unexpected error message is printed with `session->strerror`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/scope/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/time_shift_test.sh -->
# sources/storage-engines/wiredtiger/test/csuite/time_shift_test.sh

Purpose: this shell test checks that WiredTiger synchronization code uses monotonic time rather than realtime clock time. It runs `test_rwlock`, shifts apparent realtime backwards through libfaketime, and compares runtime against a baseline.

Important APIs and variables: it uses POSIX shell, `libfaketime`, `DONT_FAKE_MONOTONIC=1`, `taskset` on Linux, `DYLD_INSERT_LIBRARIES` on Darwin, `RW_LOCK_FILE` as an optional binary override, and `~/.faketimerc` as the libfaketime control file. `CPU_SET` defaults to `0-1`.

Control flow: the script validates the libfaketime library argument, resolves the `test_rwlock` binary, measures a normal run duration, then launches a second run under libfaketime. After five seconds it writes a negative offset equal to the baseline duration into `~/.faketimerc`, waits for the test, removes the faketime file, and computes percentage runtime change. A change of 20 percent or less passes.

State and persistence behavior: the only persistent side effect is temporary creation of `~/.faketimerc`, which is removed after the faketime run. The script changes environment variables for dynamic library injection and resets Darwin variables afterward.

Dependencies and integration points: it depends on libfaketime, a working `test_rwlock` binary, `taskset` on Linux, and OS-specific dynamic loader behavior. It is likely invoked manually or by a platform-specific test target because it alters user-level faketime configuration.

Risks and test signals: runtime comparison is sensitive to noisy hosts, CPU scheduling, too-small baseline durations, and missing taskset/libfaketime support. The pass/fail signal is the computed percentage difference and exit status.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/time_shift_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/main.c

Purpose: this is a comprehensive crash-recovery and backup stress test for timestamped WiredTiger workloads. It writes related data to collection, shadow, local, and oplog tables, kills the writer child after checkpoint progress, recovers the main database or backups, and verifies timestamp visibility. It also covers incremental backup, live restore, force-stopping backup cycles, model verification, disaggregated storage, prepared transactions, and repeated crash/recovery iterations.

Important APIs, types, and functions: the test uses `WT_CONNECTION`, `WT_SESSION`, `WT_CURSOR`, connection and session timestamp APIs, backup cursors/helpers, `WT_EVENT_HANDLER`, `WT_CONDVAR`, `WT_LAZY_FS`, `wt_thread_t`, and internal statistics. `THREAD_DATA` carries connection, key start, thread id, workload iteration, and random states. `REPORT` summarizes missing-key ranges. Runtime functions include `thread_run`, `thread_ts_run`, `thread_ckpt_run`, `thread_backup_run`, `backup_create_full`, `backup_create_incremental`, `backup_verify`, `recover_and_verify`, `stat_func`, `handle_conn_ready`, and `handle_conn_close`.

Control flow: `main` parses a large option set for backups, columns, compatibility, disaggregated storage, LazyFS, live restore, model verification, stress timing, thread count, timeout, iterations, and timestamp disabling. For each workload iteration it forks a child. `run_workload` opens WiredTiger with cache sized by thread count, creates tables on the first iteration, initializes condition variables, starts optional backup, checkpoint, timestamp, and writer threads, and waits forever. Writers reserve three timestamps per iteration, write collection/shadow at related timestamps, write oplog/local when not disaggregated, optionally use prepared transactions, and append `(commit_ts,durable_ts,key)` to per-thread record files. The parent waits for `checkpoint_done`, sleeps, kills the child, clears LazyFS cache if needed, removes stale `WiredTiger.backup`, and calls `recover_and_verify`.

State and persistence behavior: the test deliberately mixes durable logs, checkpoints, timestamped non-logged tables, backup directories, sidecar records, and optional page-log disaggregated metadata. `active_timestamps` allows the timestamp thread to compute a maximum stable timestamp after all workers make progress. Recovery verification uses `get=recovery` normally and `get=last_checkpoint` in disaggregated mode. For backups, records with durable timestamps newer than the backup stable timestamp are skipped. The collection and shadow tables must agree, except for the boundary where collection at timestamp `t` can survive while shadow at `t+1` is rolled back.

Dependencies and integration points: it depends heavily on WiredTiger test utilities for backup creation, live restore, model verification, LazyFS, tiered storage, disaggregated options, and work directory management. The event handler observes `WT_EVENT_CONN_READY` and `WT_EVENT_CONN_CLOSE` to run a statistics thread during recovery RTS. Smoke scripts invoke the binary across backup, live restore, in-memory, compatibility, columns, stress, and LazyFS variants.

Risks and test signals: the file protects high-risk recovery paths: rollback-to-stable correctness, prepared durable timestamp handling, checkpoint/backup races, incomplete backup discovery, disaggregated local-state wiping, and log removal interactions. Failure signals include child abnormal exit, missing stable checkpoint readiness, absent or extra records relative to stable timestamp, collection/shadow mismatch, backup verification failure, model verification failure, or assertion failures in option compatibility checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/smoke.sh

Purpose: this wrapper runs a short smoke matrix for `test_timestamp_abort`, including backup and live-restore coverage. It keeps the heavy crash-recovery workload bounded with default `-t 10 -T 5` arguments.

Important APIs and variables: it uses POSIX `sh`, `set -e`, `getopts`, `TEST_WRAPPER`, optional `-b` to pass the binary, and optional `-s` to add the C test's timing stress flag. `binary_dir` defaults to the directory containing the script and the default binary is `test_timestamp_abort`.

Control flow: the script builds `default_test_args`, resolves the binary, and runs default, column-store, backup with three iterations, backup plus live restore, in-memory, in-memory column-store, compatibility, compatibility column-store, compatibility plus in-memory, and compatibility plus in-memory column-store variants.

State and persistence behavior: the shell script itself persists nothing. Each underlying C test creates crash/recovery state, backup directories, and sidecar record files in its test home and normally cleans them up on success.

Dependencies and integration points: it integrates with the build's `make check` flow and `TEST_WRAPPER`. It intentionally comments out backup plus compatibility because the C test asserts that compatibility mode is incompatible with backup-related log record changes.

Risks and test signals: the smoke signal is exit status of each invocation. The matrix is broad but still short; long randomized stress, LazyFS, and disaggregated configurations are outside this wrapper.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/smoke_lazyfs.sh -->
# sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/smoke_lazyfs.sh

Purpose: this wrapper runs `test_timestamp_abort` with LazyFS enabled, using a longer bounded timeout than the main smoke matrix. It is targeted at crash recovery when filesystem writes may be lost from the lazy cache.

Important APIs and variables: it uses POSIX `sh`, `set -e`, `getopts`, optional `-s` for timing stress, optional `-b` for the binary path, `binary_dir` fallback, and `TEST_WRAPPER`. The default arguments are `-t 20 -T 5`.

Control flow: the script resolves the test binary, then runs two invocations: LazyFS default and LazyFS plus compatibility mode. It uses the C test's uppercase `-L` option, which explicitly enables LazyFS.

State and persistence behavior: state is owned by the underlying C test: records files, WiredTiger home, backups when configured elsewhere, and LazyFS cache state. The wrapper only sequences two invocations.

Dependencies and integration points: it requires a build and environment that support LazyFS. It shares binary-location conventions with the normal smoke wrapper and depends on `TEST_WRAPPER` for test harness concerns.

Risks and test signals: the pass signal is both invocations exiting successfully. The script does not cover backup/live-restore LazyFS combinations; it focuses on core timestamp abort recovery with and without compatibility mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/timestamp_abort/smoke_lazyfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/truncated_log/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/truncated_log/main.c

Purpose: this test validates recovery from a log file truncated in the middle of a log record. It constructs a database that has crossed into log file 2, truncates `WiredTigerLog.0000000001` inside its final record, opens with recovery, verifies that only valid records remain, and checks that a new log record can be written and read after recovery.

Important APIs, types, and functions: it uses `WT_LSN`, log cursors (`"log:"`), `WT_CURSOR`, `WT_SESSION`, process `fork`/`waitpid`, POSIX `truncate`, and WiredTiger logging configuration. `fill_db` creates the initial database and records the last log file 1 offset plus maximum key. `write_and_read_new` writes a `log_printf` message, flushes it, and walks the log cursor. `main` orchestrates child creation, truncation, recovery, verification, and cleanup.

Control flow: the child `fill_db` opens WiredTiger with small 100K log files and no sync, creates `table:main`, inserts keys until the log cursor sees records in log file 2, and writes the saved log file 1 offset and key marker into `records`. The parent reads that marker, truncates log file 1 at `offset + V_SIZE`, opens WiredTiger with recovery enabled, counts table records, then invokes `write_and_read_new`.

State and persistence behavior: the test directly mutates log persistence by truncating a WiredTiger log file after the child exits. It expects recovery to stop at the partial record, discard later invalid log records including ordinary records from log file 2, and then continue logging in a later file. The table may be row-store or column-store via `-c`.

Dependencies and integration points: it uses common test utility parsing and cleanup, a local work directory `WT_TEST.truncated-log`, and `statistics_log` for diagnostics. The smoke wrapper runs both row and column variants.

Risks and test signals: risks include incorrect offset selection, platforms with different truncate behavior, and log cursor traversal accidentally accepting invalid log file 2 records. Passing requires recovered record count not exceeding the expected valid prefix and the post-recovery log message being visible through a log cursor.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/truncated_log/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/truncated_log/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/truncated_log/smoke.sh

Purpose: this wrapper smoke-tests the truncated log recovery program in both row-store and column-store modes.

Important APIs and variables: it uses POSIX `sh`, `set -e`, an optional positional binary path, `binary_dir` fallback, and `TEST_WRAPPER`. The default binary is `test_truncated_log`.

Control flow: after resolving the binary, it runs `$TEST_WRAPPER $test_bin` and `$TEST_WRAPPER $test_bin -c`. The first exercises default string-key row-store; the second exercises recno column-store.

State and persistence behavior: the wrapper does not persist state. The C test creates, corrupts, recovers, and removes its own work directory unless preservation is requested through direct options.

Dependencies and integration points: it is intended for `make check` and assumes the script is copied near the built binary or receives the binary path as an argument.

Risks and test signals: the signal is exit status. The script only covers the two table formats; logging and recovery behavior are fixed by the C test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/truncated_log/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt10461_skip_list_stress/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt10461_skip_list_stress/main.c

Purpose: this white-box stress test reproduces WT-10461, a weak-memory-ordering hazard in skiplist insertion. It stresses `__wt_search_insert` while another thread inserts decreasing keys into the same insert list, looking for assertions that catch inconsistent `next_stack` ordering.

Important APIs, types, and functions: unlike ordinary API tests, it casts `WT_CURSOR` to `WT_CURSOR_BTREE`, sets `WT_SESSION_IMPL.dhandle`, and calls internal `__wt_search_insert` directly. It uses `WT_ITEM` for the probe key, `__wt_thread_create`, atomic counters, `sysconf(_SC_NPROCESSORS_ONLN)`, and `debug_mode=(stress_skiplist=1)`. `insert_key` wraps normal cursor inserts. `thread_search_insert_run` repeatedly builds the search insert stack for key `"00"`. `run` sets up and stresses one insert list.

Control flow: `main` loops `run` for about fifteen minutes. Each run creates a fresh database, creates a table with huge `memory_page_max` to avoid page splitting, inserts boundary keys `"0"` and `"99999"`, starts one search-insert thread per CPU except one, waits until they are active, then inserts 10,000 keys in decreasing order inside one transaction. Search-insert threads stop when `inserts_finished` becomes true.

State and persistence behavior: persistence is not the point; each run creates and removes a temporary home. The important state is in-memory insert list and skiplist pointer ordering under concurrent access. The test intentionally avoids actually inserting the `"00"` probe key in search threads.

Dependencies and integration points: this file depends on WiredTiger internal structures and functions, not just the public API. It also depends on debug stress mode and CPU parallelism to increase race probability. The smoke wrapper runs the binary once, but the binary itself loops for its timed duration.

Risks and test signals: the main risk is relying on internal layout and timing, so it may be expensive or architecture-sensitive. Passing is no assertion or crash for the full duration. A failure usually manifests as an internal assertion in `__wt_search_insert` or related skiplist code.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt10461_skip_list_stress/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt10461_skip_list_stress/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/wt10461_skip_list_stress/smoke.sh

Purpose: this wrapper runs the WT-10461 skip list stress binary as a smoke test.

Important APIs and variables: it uses POSIX `sh`, `set -e`, optional positional binary path, `binary_dir` fallback, and `TEST_WRAPPER`. The default binary name is `wt10461_skip_list_stress`.

Control flow: it resolves the binary and executes a single wrapped invocation. The duration and workload are controlled by the C program, which loops internally for roughly fifteen minutes.

State and persistence behavior: the shell script owns no state. Each C test iteration creates and removes its own WiredTiger home.

Dependencies and integration points: it relies on the build system naming this binary without a `test_` prefix, unlike many other csuite wrappers. It is intended to be called by `make check` or a targeted test suite.

Risks and test signals: because the binary is time-based and CPU-parallel, runtime can be long. The only wrapper-level signal is nonzero exit if the binary asserts, crashes, or returns failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt10461_skip_list_stress/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt10897_compact_quick_interrupt/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt10897_compact_quick_interrupt/main.c

Purpose: this regression test verifies that compact can be interrupted quickly through the general event handler before doing meaningful work, and that a no-work compact reports as skipped rather than interrupted.

Important APIs, types, and functions: it uses `WT_EVENT_HANDLER` with both message and general callbacks, `WT_EVENT_COMPACT_CHECK`, `WT_SESSION::compact`, data-source statistics cursor, and `WT_STAT_DSRC_BTREE_COMPACT_PAGES_REVIEWED`. `populate` inserts random values and a large string payload. `remove_records` creates free space. `message_handler` detects verbose compact messages for "skipping compaction" and "compact interrupted". `handle_general` returns `-1` to interrupt when configured.

Control flow: `main` creates `table:compact`, inserts a small set of records, checkpoints, and runs compact expecting a skipped-compaction message. It then inserts many more records, checkpoints, removes about half the key range, enables interruption, and calls compact again. That call must return `WT_ERROR`, set the interrupted flag, and not set skipped. The test then reads the compact pages reviewed statistic and asserts it is zero. Finally it disables interruption and runs a normal compact successfully.

State and persistence behavior: the test creates a temporary home with 2GB cache and verbose compact logging. It persists enough table data and checkpoints to make compact eligible for real work, then verifies interruption before page review. It removes the home unless preservation is requested.

Dependencies and integration points: it depends on compact verbose messages and data-source statistics names remaining stable. It also depends on the general event callback being invoked early enough in compaction.

Risks and test signals: risks include message text changes, statistic semantics changes, or compaction doing work before the interrupt check. Passing requires the exact assertions around skipped/interrupted flags, return code, and zero pages reviewed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt10897_compact_quick_interrupt/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt11126_compile_config/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt11126_compile_config/main.c

Purpose: this program is both a correctness test and benchmark for WiredTiger compiled configuration strings, specifically for `WT_SESSION.begin_transaction`. It compares formatting on every call, choosing prebuilt strings, binding values into one compiled configuration, choosing among many compiled configurations, and null configuration.

Important APIs, types, and functions: key APIs are `WT_CONNECTION::compile_configuration`, `WT_SESSION::bind_configuration`, `WT_SESSION::begin_transaction`, and `WT_SESSION::rollback_transaction`. It also inspects `WT_SESSION_IMPL` and `WT_TXN` flags to verify config effects. `THREAD_OPTS` passes shared compiled config pointers and timing buffers to benchmark threads. Initialization helpers include `begin_transaction_medium_init`, `begin_transaction_fast_init`, and `begin_transaction_fast_alternate_init`. `do_config_run` runs one variant for `N_CALLS`.

Control flow: `main` parses test options and thread count, opens WiredTiger, initializes all precomputed/compiled configurations, starts benchmark threads, waits for them, then prints nanoseconds per begin/rollback pair and speed relative to baseline. Each thread loops `N_RUNS` times across all variants. For the first run, non-null variants verify that internal transaction flags match random `ignore_prepare`, `roundup_timestamps`, and `no_timestamp` values.

State and persistence behavior: no user table is created; the persistent database is just a temporary WiredTiger home used to own a connection and sessions. The main state under test is compiled configuration lifetime across the connection and per-session transaction flags after begin/rollback cycles.

Dependencies and integration points: it depends on WiredTiger's internal transaction flag definitions and compiled configuration API. It is useful as a performance benchmark but has assertions that make it a correctness test as well.

Risks and test signals: benchmark numbers are environment-sensitive, but pass/fail comes from API return checks and flag assertions. Risk areas include compiled config lifetime, binding type mismatches, and internal flag changes not reflected in the test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt11126_compile_config/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt11440_config_check/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt11440_config_check/main.c

Purpose: this benchmark-style correctness test compares two caller-side strategies for `begin_transaction` configuration strings: formatting a string every call and choosing among preformatted strings. It validates that both produce the same transaction flag effects for a MongoDB-like four-variable configuration.

Important APIs, types, and functions: it uses `WT_SESSION::begin_transaction`, `WT_SESSION::rollback_transaction`, internal `WT_SESSION_IMPL` and `WT_TXN` flag checks, random config selection, and a table of implementation variants. `begin_transaction_base` formats with `__wt_snprintf`. `begin_transaction_advance_format_init` prepares all 24 combinations of `ignore_prepare`, `roundup_timestamps.prepared`, `roundup_timestamps.read`, and `no_timestamp`; `begin_transaction_advance_format` selects one.

Control flow: `main` opens a temporary connection/session, initializes variant data, then alternates variants for `N_RUNS`. `do_config_run` runs `N_CALLS` begin/rollback pairs with random config booleans, optionally checks internal flags on the first run, and accumulates elapsed nanoseconds. The program prints total and per-call timing plus speed relative to the base variant.

State and persistence behavior: the database home exists only to hold a WiredTiger connection and session. There is no application table state. The relevant mutable state is the active transaction configuration flags that are reset by rollback after each call.

Dependencies and integration points: it depends on test utility setup, `statistics_log`, internal transaction flags, and stable configuration option names for `begin_transaction`.

Risks and test signals: timing is not deterministic, so correctness assertions are the meaningful test signal. If config parser semantics or internal flag names change, this test needs updates. A passing run completes all calls and prints benchmark lines.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt11440_config_check/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt12015_backup_corruption/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt12015_backup_corruption/main.c

Purpose: this crash harness verifies that incremental backup metadata remains safe when WiredTiger crashes during checkpoint/turtle update or during backup force-stop processing. After the injected crash, it reopens the database, creates another backup using recovered backup IDs, and verifies backup self-consistency.

Important APIs, types, and functions: it uses `WT_CONNECTION`, `WT_SESSION`, backup helpers `testutil_backup_create_full`, `testutil_backup_create_incremental`, `testutil_backup_force_stop`, backup query cursor `"backup:query_id"`, failpoint reconfiguration `debug=(checkpoint_fail_before_turtle_update=true)`, process `fork`, `waitpid`, and signal handling. Main helpers are `populate_table`, `verify_backup`, `do_work_before_failure`, `do_work_after_failure`, `run_test_backup`, and `run_test_force_stop`.

Control flow: `main` parses options, chooses logged or no-log environment config, creates a work home, installs a SIGCHLD handler, and runs scenario 1, scenario 2, or both. In each scenario a child creates the database, table, several full/incremental backups and checkpoints, enables the checkpoint failpoint, creates `expect_abort`, and then calls either checkpoint or backup force-stop expecting the process to abort. The parent waits for the crash, copies the database for debugging, reopens, queries available backup IDs, populates more data, creates a new full or incremental backup, closes, and verifies that backup.

State and persistence behavior: the test persists `backup.N` directories, a `check` directory for verification copies, a `save` copy of the crashed database, and an `expect_abort` sentinel used to suppress expected abort messages. Table data encodes key/value self-consistency by storing `k` in the key suffix and bitwise complement in the value. Verification opens a copied backup and checks every row satisfies `k == ~v`.

Dependencies and integration points: it depends on WiredTiger backup ID metadata, turtle-file update ordering, logging or no-logging environment variants, and test utility backup helpers. It integrates with process-level crash testing and event-handler filtering for expected panic/abort text.

Risks and test signals: critical risks are selecting the wrong recovered backup source ID after a crash, leaving incomplete backup metadata visible, or producing a corrupt incremental backup. Passing requires child death at the expected failpoint, successful reopen, successful follow-on backup, and complete self-consistency verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt12015_backup_corruption/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt13867_interrupt_eviction_handler/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt13867_interrupt_eviction_handler/main.c

Purpose: this test verifies that application eviction callbacks can interrupt eviction and that WiredTiger statistics classify interrupted application cache operations as busy/uninterruptible rather than idle/interruptible.

Important APIs, types, and functions: it uses a `WT_EVENT_HANDLER` general callback for `WT_EVENT_EVICTION`, a tiny `cache_size=1MB`, connection statistics, and internal statistic keys `WT_STAT_CONN_APPLICATION_CACHE_OPS`, `WT_STAT_CONN_APPLICATION_CACHE_UNINTERRUPTIBLE_OPS`, `WT_STAT_CONN_APPLICATION_CACHE_INTERRUPTIBLE_OPS`, `WT_STAT_CONN_CACHE_BYTES_MAX`, and `WT_STAT_CONN_CACHE_BYTES_INUSE`. `populate` inserts random keys with 1KB values to create cache pressure. Macros `GET_STAT`, `GET_STATS`, and `GET_ALL_STATS` collect counters.

Control flow: `main` opens the database, creates `table:evict`, records the application session in `my_session`, and first populates until enough cache operations occur without interruption. It asserts the eviction callback ran, both busy and idle counters sum to total cache operations, and cache size stats are nonzero. It then enables `do_interrupt_eviction`, populates again until enough additional cache operations occur, and asserts busy operations increased while idle operations did not.

State and persistence behavior: the table persists only within a temporary home. The durable data is less important than forcing cache pressure and eviction. The core mutable state is the event-handler return value and the connection statistics counters.

Dependencies and integration points: it relies on eviction event callbacks being delivered to the application session rather than internal sessions, verified by `session == my_session`. It also relies on stable statistics semantics for application cache operation classification.

Risks and test signals: risk areas include cache pressure being insufficient on a platform, event callbacks changing session attribution, or statistics names/meanings changing. The loops double work up to a bounded cycle count to reduce flakiness. Passing requires all assertions and cleanup to complete.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt13867_interrupt_eviction_handler/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt16990_disagg_checkpoint_panic/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt16990_disagg_checkpoint_panic/main.c

Purpose: this process-level regression test verifies that a disaggregated storage checkpoint error during shared metadata queue processing triggers `WT_PANIC`. The panic is required because metadata has already been written and continuing could risk corruption.

Important APIs, types, and functions: it uses disaggregated storage options from `TEST_OPTS`, `block_manager=disagg` table configuration, `WT_CONNECTION::reconfigure` with `timing_stress_for_test=[failpoint_disagg_checkpoint_queue_drain]`, `WT_CONNECTION::set_timestamp`, checkpoints, and a custom error handler. `panic_event_handler` writes errors to stderr and exits cleanly on `WT_PANIC`. `subtest_run` performs the child workload. `main` forks and verifies child status plus stderr contents.

Control flow: `main` parses build/home/preserve/disagg flags, sets `page_log_home`, recreates the home, and forks. The child disables core files, redirects stderr to `stderr.txt`, opens WiredTiger with the panic handler, creates and populates a disaggregated file, sets stable timestamp 10, and checkpoints successfully. It then enables the failpoint, creates/populates a second disaggregated file to ensure shared metadata queue entries exist, sets stable timestamp 20, and checkpoints expecting panic. The parent waits, requires a clean success exit from the panic handler, then scans `stderr.txt` for the expected message fragment.

State and persistence behavior: the test persists disaggregated page-log state in the test home and an stderr capture file. It deliberately does not inspect recovered data; it validates that the failure mode is panic rather than silent continuation.

Dependencies and integration points: it depends on disaggregated storage being enabled through test options, the failpoint name, the panic error path, and the specific diagnostic message "failed while processing shared metadata queue".

Risks and test signals: message text changes can cause false failures even if panic occurs. The child uses `_exit` from the event handler to avoid diagnostic abort handling. Passing requires no child signal, exit success, and the expected panic text in stderr.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt16990_disagg_checkpoint_panic/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt1965_col_efficiency/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt1965_col_efficiency/main.c

Purpose: this workload demonstrates the WT-1965 column-store inefficiency involving sparse record IDs. It is primarily a performance/efficiency regression test rather than a correctness oracle.

Important APIs, types, and functions: it uses `WT_SESSION`, `WT_CURSOR`, pthreads, column-store `key_format=r`, fixed-width `Q` value fields, a secondary `table:index`, and common test options. `thread_func` is the workload function. It uses an atomic fetch-add on `opts->next_threadid` to assign thread indexes and a global timestamp counter `g_ts`.

Control flow: `main` opens a 1GB-cache logged database with eviction/checkpoint tuning, builds a value format containing eight `Q` fields, creates the primary sparse recno table and an index table, starts four threads, joins them, then scans the primary table. Each thread inserts records whose recnos are `ins_thr_idx << 40 | ins_rotor`, creating huge key gaps. Each insert also writes an index row keyed by object id and timestamp, then mutates two fields in its per-object data array and sleeps to approximate 5K updates/sec.

State and persistence behavior: the test persists sparse recno records and index records in a temporary home. It does not crash or recover. The value state is a timestamp plus eight counters per object, where counters change gradually between insert rotations.

Dependencies and integration points: it relies on WiredTiger handling very sparse column-store record numbers efficiently enough to finish. Verbose mode prints decoded records for inspection.

Risks and test signals: there is no explicit performance threshold, so failure is usually timeout, excessive CPU, assertion, or API error. The global `g_ts` is incremented without synchronization beyond the workload's loose benchmarking intent, so it should not be treated as a strict correctness timestamp source.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt1965_col_efficiency/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2246_col_append/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt2246_col_append/main.c

Purpose: this WT-2246 performance regression test stresses column-store append cursors. It targets an inefficiency where append cursor record-number allocation searched the target leaf page unnecessarily.

Important APIs, types, and functions: it uses WiredTiger append cursors (`open_cursor(..., "append", ...)`), recno `key_format=r`, string values, test utility append thread `thread_append`, signal handling, and test option fields such as `n_append_threads`, `nrecords`, and `max_inserted_id`. `page_init` preloads enough records to create existing pages before the timed append workload. `onsig` flips `opts->running` on SIGINT.

Control flow: `main` sets defaults of six append threads and 20 million records, opens a 2GB-cache database with eviction threads, creates a column-store table, and calls `page_init(5000)`. It then closes and reopens the connection to force state to disk, installs SIGINT handling, starts append worker threads, joins them, and prints processor seconds per million records inserted.

State and persistence behavior: the test persists a column-store table with appended string records. `page_init` obtains allocated record numbers through `cursor->get_key` after each append and stops after reaching the target. The main workload advances `opts->max_inserted_id` through shared test utility append code.

Dependencies and integration points: it depends on shared csuite test utility code providing `thread_append` and interpreting `TEST_OPTS` fields. It is benchmark-like and integrates with general table type and home parsing.

Risks and test signals: there is no hard assertion on performance. Regression signal is excessive runtime or CPU use, while correctness failures appear as API errors or thread failures. Because it relies on time/CPU output, comparisons should be made under controlled conditions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2246_col_append/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2535_insert_race/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt2535_insert_race/main.c

Purpose: this test reproduces WT-2535 by checking for lost updates when many threads repeatedly read-modify-write the same record. It is a correctness test: the final value must equal `nthreads * nrecords`.

Important APIs, types, and functions: it uses `WT_SESSION` snapshot transactions, `WT_CURSOR::search`, `WT_CURSOR::update`, `WT_ROLLBACK` retry handling, pthreads, and an atomic readiness barrier. `get_value` wraps the variadic cursor getter for a `uint64_t` value. `thread_insert_race` performs the concurrent increment loop. `main` creates the single-record table and verifies the final value.

Control flow: `main` defaults to 20 threads and 100,000 operations per thread, parses options including row or column table type, creates the table with `value_format=Q`, inserts key 1 with value 0, starts all threads, joins them, then reads key 1 and compares it to the expected count. Each worker opens its own session/cursor, waits until all workers are ready, then loops. On each iteration it begins a snapshot transaction, reads the current value, updates it to `value + 1`, commits, and retries the same iteration if update returns `WT_ROLLBACK`.

State and persistence behavior: the durable state is a single integer record in a temporary WiredTiger table. The readiness barrier uses `ready_counter` with memory barriers so the race starts concurrently. Transaction retry behavior is the key state transition: rollbacks must not lose an increment because the loop decrements `i` and retries.

Dependencies and integration points: the smoke wrapper runs both row and column variants via `-t r` and `-t c`. The test uses common parse/cleanup helpers and statistics logging.

Risks and test signals: failure is explicit if the final value is not exactly expected. Other risks include starvation from repeated rollback under high contention, missing cursor/session cleanup in worker threads, or table-type option changes. Passing prints the operation count and elapsed processor seconds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2535_insert_race/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2535_insert_race/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/wt2535_insert_race/smoke.sh

Purpose: this wrapper runs the WT-2535 insert race test in both supported table layouts.

Important APIs and variables: it uses POSIX `sh`, `set -e`, optional positional binary path, `binary_dir` fallback, and `TEST_WRAPPER`. The default binary is `test_wt2535_insert_race`.

Control flow: after resolving the binary, it runs `$TEST_WRAPPER $test_bin -t r` for row-store and `$TEST_WRAPPER $test_bin -t c` for column-store. The C test supplies its own default thread and operation counts.

State and persistence behavior: no wrapper state is persisted. The C test creates a temporary table, performs concurrent updates to one record, validates the final value, and cleans up on success.

Dependencies and integration points: it assumes the test utility `-t` table-type option accepts `r` and `c`. It is intended for make-check style execution through `TEST_WRAPPER`.

Risks and test signals: the wrapper signal is exit status. It provides focused row/column correctness coverage but does not vary thread count, record count, or cache settings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2535_insert_race/smoke.sh -->
