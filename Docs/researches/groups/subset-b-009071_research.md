# subset-b-009071 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/rollback_to_stable_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/rollback_to_stable_util.py

Purpose: Shared base support for rollback-to-stable Python tests. It supplies repeatable bulk update/modify/remove helpers, read-at-timestamp validation, eviction forcing, and a teardown verifier that runs the RTS log verifier against `stdout.txt`.

Important APIs and types: `get_git_root`, `get_rts_verify_path`, and `verify_rts_logs` locate and run `tools/rts_verifier/rts_verify.py`. `test_rollback_to_stable_base` extends `wttest.WiredTigerTestCase`, ignores RTS/read verbose output, installs `verify_rts_logs` as a teardown action, and exposes `retry_rollback`, `large_updates`, `large_modifies`, `large_removes`, `check`, and `evict_cursor`.

Control flow: Tests subclass the base, use `large_*` helpers to write many keys under normal, no-timestamp, or prepared timestamped transactions, then call WiredTiger rollback-to-stable APIs elsewhere. `retry_rollback` reruns a callable up to 100 times on `WT_ROLLBACK`, rolling back and reopening a transaction when a session is supplied. `check` scans at a read timestamp and verifies value/count invariants.

State and persistence behavior: The helper mutates real WiredTiger tables and timestamps commits using `timestamp_str`. Prepared updates use prepare, commit, and durable timestamps. `evict_cursor` opens `debug=(release_evict)` and resets periodically inside an `ignore_prepare=true` transaction to push data out of cache before rollback-to-stable validation. The teardown verifier treats stdout verbose logs as a persistent test signal.

Dependencies and integration points: Depends on `wiredtiger`, `wttest`, `WT_ROLLBACK` error strings, the RTS verifier script, and dataset objects that provide `key(i)`. It integrates with the suite teardown-action contract in `WiredTigerTestCase`.

Risks: Retry detection depends on localized/stringified rollback messages. A failed helper operation can leave an open transaction unless the rollback branch runs. The verifier path falls back relative to this helper if Git discovery fails, so repository layout changes can break teardown verification.

Test signals: Successful tests have no RTS verifier errors, expected row counts at read timestamps, exact values after rollback-to-stable, and no exhausted retry loops.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/rollback_to_stable_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/suite_subprocess.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/suite_subprocess.py

Purpose: Mixin for WiredTiger suite tests that need to run subprocesses, especially `run.py` test functions and the external `wt` utility, while preserving suite-style output checks and diagnostics.

Important APIs and types: `suite_subprocess` exposes file-output assertions (`has_error_in_file`, `check_no_error_in_file`, `check_file_content`, `check_file_contains`, `check_file_not_contains`, `check_empty_file`, `check_non_empty_file`), regex helper `convert_to_pattern`, diagnostic `show_outputs`, `run_subprocess_function`, and `runWt`.

Control flow: `run_subprocess_function` builds a `run.py -p --dir <directory> dotted.test.method` command, captures stdout/stderr in parent-directory files, optionally reports failures, and returns the exit status plus the generated WiredTiger home. `runWt` closes the live connection when requested, chooses `.libs/wt` when available, optionally wraps it in gdb/lldb, runs with input/output redirection, enforces expected success or failure, checks default output files are empty, and reopens the test connection/session.

State and persistence behavior: Subprocess calls create `subprocess.out`, `subprocess.err`, `wt.out`, `wt.err`, and test home directories. `runWt` forces flushability by closing the connection before external access and may rewrite verify URIs to `layered:` when the disagg hook is active.

Dependencies and integration points: Imports `wt_builddir` from `run.py`, `WiredTigerTestCase`, `wttest`, Python `subprocess`, and hook state such as `hook_names`. It is mixed into classes like backup tests and uses `close_conn`/`open_conn` supplied by `WiredTigerTestCase`.

Risks: File checks cap reads at 1 GiB but still can be expensive. Error detection is string based. `runWt` is skipped for tiered hooks because external utility invocation cannot reproduce injected tiered extension configuration. Debugger modes change normal capture behavior.

Test signals: Exit-code assertions, empty/non-empty output files, regex/content matches, and printed captured output on failure provide the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/suite_subprocess.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/sweep_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/sweep_util.py

Purpose: Small base class for tests that must wait for WiredTiger data-handle sweep activity without spinning until the global task timeout.

Important APIs and types: `sweep_util` extends `wttest.WiredTigerTestCase` and provides `wait_for_sweep(baseline=None, increment=1, statistic=stat.conn.dh_sweeps, session=None, timeout=60, poll_interval=0.5)`.

Control flow: The method samples the chosen statistics cursor value when no baseline is supplied, then repeatedly opens `statistics:`, reads the statistic tuple value, and returns once the value has advanced by `increment`. Between polls it asserts the timeout has not elapsed and sleeps for the configured interval.

State and persistence behavior: It does not mutate data directly; it observes connection statistics maintained by WiredTiger. Each poll opens and closes a statistics cursor through `wttest.open_cursor`, so cursor lifetime is bounded even on assertion failures.

Dependencies and integration points: Depends on `wiredtiger.stat`, suite cursor context manager `wttest.open_cursor`, and the caller's session. Tests can override the statistic to wait for other sweep-related counters.

Risks: Timing remains environment-sensitive because sweep is asynchronous. Too-small timeouts can fail slow machines, while too-large intervals delay failure. If the connection has statistics disabled, the helper cannot observe the expected signal.

Test signals: The returned observed counter value and timeout assertion message show whether the sweep server advanced enough within the expected window.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/sweep_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtbackup.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wtbackup.py

Purpose: Shared base class for full, selective, log, and incremental backup tests. It builds test data, copies files returned by backup cursors, applies block-range incremental copies, and compares backup homes through the `wt` utility.

Important APIs and types: `backup_base` extends `wttest.WiredTigerTestCase` and `suite_subprocess`. Key methods include `backup_get_stat`, `add_data`, `populate`, `setup_directories`, `confirmPathDoesNotExist`, `copy_file`, `take_selective_backup`, `take_full_backup`, `compare_backups`, `range_copy`, `take_incr_backup_block`, `take_log_backup`, and `take_incr_backup`.

Control flow: Tests populate objects, checkpoint when needed, open a `backup:` cursor, and iterate with `next()`/`get_key()` because backup cursors do not expose values. Full/selective backup copies complete files. Incremental backup opens a top-level cursor with `src_id`/`this_id`, then duplicate cursors with `incremental=(file=...)`; file records are copied whole and range records are copied with seek/read/write.

State and persistence behavior: The helper manages `WT_TEST_TMP`, full backup directories, incremental backup directories, optional log subdirectories, and copied WiredTiger files. It tracks backup IDs and multiplier counters to create unique data across iterations. Incremental range copies update an existing backup image in place and verify changed block content in consolidate mode.

Dependencies and integration points: Uses WiredTiger backup cursor semantics, `wiredtiger.WT_BACKUP_FILE`, `WT_BACKUP_RANGE`, connection/data-source backup statistics, `helper.compare_files`, and `suite_subprocess.runWt` for dump/verify comparisons.

Risks: Path handling assumes backup cursor keys map cleanly to local files and optional log paths. Incremental correctness depends on correct cursor ordering and stats updates. Range-copy assertions can be too strict unless consolidate mode is used because unchanged blocks may be reported separately.

Test signals: Backup cursor open/duplicate stats, range block stats, copied file lists and sizes, `wt dump` comparisons, `wt verify`, missing-URI checks, and nonzero changed-block counters validate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtbackup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtbound.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wtbound.py

Purpose: Common utilities for cursor-bound tests across key/value formats, indexes, column groups, forward/reverse traversal, inclusive/exclusive bounds, and evicted pages.

Important APIs and types: `set_prefix_bound` sets lower/upper string prefix bounds. `bound` and `bounds` model expected bound state and range membership. `bound_base` extends `wttest.WiredTigerTestCase` with table creation, key/value generation, bound setting, and traversal checking methods.

Control flow: `create_session_and_cursor` creates the table, optional column groups or index metadata, populates keys from `start_key` to `end_key`, optionally evicts pages with `debug=(release_evict)`, and returns a cursor. `set_bounds` sets a generated key and calls `cursor.bound`. `cursor_traversal_bound` walks `next` or `prev`, checks `WT_NOTFOUND`, validates every returned key against inclusive/exclusive limits, and compares the observed count to either an explicit count or the computed range.

State and persistence behavior: It persists a table, optional colgroups, and optional indexes in the test home. State flags such as `lower_inclusive`, `upper_inclusive`, `use_index`, and `use_colgroup` define expected traversal semantics. Eviction alters cache residency but not logical data.

Dependencies and integration points: Depends on `wiredtiger`, `wttest.recno`, cursor bound API strings, and tests that provide `uri`, `file_name`, `key_format`, `value_format`, `direction`, and `evict`.

Risks: Expected range math is integer-oriented and must match generated keys for compound/string/raw formats. Prefix-bound string increment only handles simple last-character advancement. Index population temporarily toggles `use_index`, so subclass state misuse can produce wrong expectations.

Test signals: Bound API return codes, traversal counts, ordered key comparisons, and `WT_NOTFOUND` termination provide the main assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtbound.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtdataset.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wtdataset.py

Purpose: Reusable test dataset abstractions for creating, populating, updating, and verifying simple and complex WiredTiger tables with optional indexes, column groups, timestamped writes, and tiered-storage population split points.

Important APIs and types: `BaseDataSet`, `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `TrackedComplexDataSet`, `TrackedSimpleDataSet`, and helpers `simple_key`, `simple_value`, `complex_key`. Core methods include `create`, `open_cursor`, `truncate`, `store_range`, `fill`, `populate`, `key_by_format`, `value_by_format`, `check`, `check_cursor`, and tracked `store_count`.

Control flow: A dataset is constructed with a testcase, URI, row count, formats, and config. `populate` optionally creates schema, fills rows through a timestamped cursor, and creates post-fill indexes when needed. `store_range` can force `flush_tier` or reopen the connection at hook-provided row percentages. `check` scans the cursor and delegates format-specific verification.

State and persistence behavior: The classes create tables, indexes, and colgroups in WiredTiger metadata and insert deterministic key/value rows. Tracked datasets maintain in-memory dictionaries recording how many times each key was stored, allowing expected values to vary across updates and large-value multipliers. Timestamped cursors may wrap every mutation in timestamped transactions when the timestamp hook supplies a generator.

Dependencies and integration points: Integrates with `wttimestamp.TimestampedCursor`, `WiredTigerTestCase` platform APIs for timestamps and tiered percentages, and many suite tests that need canonical data fixtures.

Risks: In-memory tracked state is authoritative for verification and can diverge if a test mutates data outside the dataset object. Tiered hook reopen behavior closes cursors mid-population and depends on testcase connection lifecycle. Complex index/colgroup assumptions are sensitive to schema-string changes.

Test signals: Exact key order, row counts, value equality, index lookup correctness, and tracked dictionary exhaustion verify data integrity.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtdataset.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wttest.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wttest.py

Purpose: Central Python test harness for WiredTiger suite tests. It owns global suite setup, per-test directories, connection/session lifecycle, output capture expectations, hook platform APIs, rollback retry behavior, teardown cleanup, backup convenience, statistics helpers, and parallel suite execution.

Important APIs and types: `ReadonlySimpleNamespace`, `timeout`, `TestSuiteConnection`, `ExtensionList`, and `WiredTigerTestCase` are the main types. Important methods include `globalSetup`, `finalReport`, `setUpConnectionOpen`, `wiredtiger_open`, `setUpSessionOpen`, `open_conn`, `reopen_conn`, `transaction`, `setUp`, `tearDown`, `backup`, output expectation context managers, exception helpers, `retryEBUSY`, `compactUntilSuccess`, `dropUntilSuccess`, `verifyUntilSuccess`, `checkpoint_and_verify_stats`, and module-level decorators/functions such as `open_cursor`, `longtest`, `extralongtest`, `prevent`, `skip_for_hook`, `only_for_hook`, `runsuite`, and `run`.

Control flow: `globalSetup` stores command-line variables, initializes hook manager, test directory, IO capture, randomness, and suite flags. `setUp` creates a unique test directory, enters it, opens a connection/session with statistics and extensions, and records the current testcase in thread-local storage. `_callTestMethod` wraps test execution with optional timeout and retries `WiredTigerRollbackError`. `tearDown` runs registered actions, hook teardown, optional layered verification, closes all tracked connections, validates captured output, deletes or preserves the directory, and reports failures.

State and persistence behavior: The harness creates `WT_TEST` subdirectories, `testname.txt`, `results.txt`, stdout/stderr capture files, and WiredTiger home files. `TestSuiteConnection` tracks open connections in `_connections` so teardown can close leaked handles. Static class state records seeds, verbosity, hook names, retry counts, and command-line vars.

Dependencies and integration points: Integrates with `abstract_test_case`, `test_result`, `wthooks`, `wtscenario`, WiredTiger Python bindings, `concurrencytest`, extension libraries under the build directory, and hook platform APIs for tiered/disagg/timestamp behavior.

Risks: It relies heavily on global/class state and thread-local current testcase, so parallelism and hooks must be disciplined. Output checking can create secondary failures after a primary error unless ignored. Retry-on-rollback hides transient failures but reports excessive aggregate retry rates. Extension config construction is string-sensitive.

Test signals: Suite result status, captured stdout/stderr checks, teardown action return tuples, connection-close success, layered verification, statistics deltas, retry counters, and preserved directories on failure are the key signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wttest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtthread.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wtthread.py

Purpose: Thread helpers for tests that need concurrent checkpoints, tier flushes, backups, or mixed table operations while retaining access to the current `WiredTigerTestCase`.

Important APIs and types: `Thread` wraps `threading.Thread` and installs the captured current testcase in thread-local storage before running. Worker classes include `checkpoint_thread`, `named_checkpoint_thread`, `flush_checkpoint_thread`, `backup_thread`, and `op_thread`.

Control flow: Checkpoint threads open their own sessions and loop until a `done` event is set, optionally stopping after `checkpoint_count_max`. `flush_checkpoint_thread` randomly chooses normal checkpoint or `flush_tier=(enabled)`. `backup_thread` periodically rebuilds a backup directory, copies files from a backup cursor, opens the backup home, and compares live and backup tables. `op_thread` drains a queue of operation tuples for group insert/update, insert, session bounce, drop, or create-table-and-insert.

State and persistence behavior: Threads create independent sessions on a shared connection. Backup threads delete/recreate backup directories and copy WiredTiger files. Operation threads mutate tables and metadata concurrently. `checkpoint_count` records progress for bounded checkpoint tests.

Dependencies and integration points: Uses `wiredtiger`, `wttest`, `helper.compare_tables`, Python `queue`, `threading.Event`, and the suite thread-local current testcase used by hooks/utilities.

Risks: Threads swallow some `WiredTigerError` cases intentionally during drop/create races, which can hide unexpected errors if tests do not assert final state. Backup verification assumes file URIs from copied files and skips `WiredTiger*` metadata names. Fast checkpoint loops can amplify timing sensitivity.

Test signals: Thread completion, checkpoint counters, queue drain/task_done behavior, backup/live table comparisons, and absence of unhandled thread exceptions provide validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtthread.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wttimestamp.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wttimestamp.py

Purpose: Lightweight timestamping layer used by the timestamp hook and dataset helpers to transparently timestamp cursor mutations.

Important APIs and types: `WiredTigerTimeStamp` stores a monotonically increasing integer with `incr`, `get_incr`, and `get`. `session_timestamped_transaction` is a context manager that begins/commits or timestamps an existing transaction. `TimestampedCursor` proxies a `wiredtiger.Cursor` and overrides `insert`, `update`, `remove`, and `modify`.

Control flow: When a timestamp generator exists and the session is not already in a transaction, the context manager begins a transaction, yields to the operation, then commits with `commit_timestamp=<next>`. If a transaction is already active, it yields and then calls `timestamp_transaction` with the next timestamp. `TimestampedCursor` delegates all other methods to the wrapped cursor via `__getattr__`.

State and persistence behavior: Timestamp state is in-memory per `WiredTigerTimeStamp`. Persistent behavior is in commit timestamps applied to WiredTiger updates. The cursor wrapper initializes `session._has_transaction` if missing, while the timestamp hook keeps that flag accurate by replacing transaction APIs.

Dependencies and integration points: Used by `wtdataset.BaseDataSet.open_cursor` and `truncate`, and supplied through `hook_timestamp.TimestampPlatformAPI`. Depends on WiredTiger session transaction/timestamp APIs and testcase timestamp formatting expectations.

Risks: Correct behavior depends on `_has_transaction` being maintained by hooks; without it, nested transaction detection can be wrong. The timestamp counter is simple and not synchronized for multi-threaded mutation. Exceptions inside the yielded operation do not explicitly roll back.

Test signals: Timestamped dataset tests should see commits at increasing timestamps, stable reads at selected timestamps, and no nested transaction errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wttimestamp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_demo.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_demo.py

Purpose: Demonstration hook showing how the WiredTiger Python test hook framework can alter open arguments, observe API results, and replace session methods.

Important APIs and types: Hook functions include `wiredtiger_open_args`, `wiredtiger_open_notify`, `session_open_cursor_notify`, and `session_create_replace`. `DemoHookCreator` extends `wthooks.WiredTigerHookCreator`, and `initialize` returns a creator instance.

Control flow: `setup_hooks` retrieves the original `Session.create`, registers an argument hook on `wiredtiger_open` to append cache size, a notify hook after `wiredtiger_open`, a replacement hook for `Session.create`, and a notify hook on `Session.open_cursor`. The replacement create behavior depends on the numeric hook argument: normal create, create then drop, or create/drop/create.

State and persistence behavior: Mode 1 deliberately removes newly created objects; mode 2 recreates them. Debug messages go to `/dev/tty` via `WiredTigerTestCase.tty` to avoid polluting captured stdout/stderr.

Dependencies and integration points: Exercises `wthooks` hook registration and the global monkey-patched WiredTiger bindings. It is launched by `run.py --hook demo=N` and uses `WiredTigerTestCase` only for debug output.

Risks: It is intentionally disruptive in some modes and can make normal tests fail. It demonstrates that replacement hooks must preserve original method signatures and that multiple assignments to one method add hook behavior rather than replace prior hook metadata.

Test signals: The signal is behavioral: hook debug output on the terminal and expected pass/fail behavior depending on the mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_demo.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_disagg.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_disagg.py

Purpose: Hook that runs ordinary Python tests against disaggregated/layered storage by injecting page-log configuration, translating eligible table URIs, and skipping unsupported operations.

Important APIs and types: `wiredtiger_open_replace`, URI helpers `mark_as_layered`, `is_layered`, `replace_uri`, replacements for session `alter`, `checkpoint`, `compact`, `create`, `drop`, `open_cursor`, `salvage`, `truncate`, and `verify`, `DisaggHookCreator`, and `DisaggPlatformAPI`.

Control flow: The open replacement validates page-log/key-provider extensions, rejects incompatible connection configs, merges `verbose=[layered]`, builds `disaggregated=(role=...,page_log=...)`, loads extensions, records leader/follower role on the testcase, calls original open, and ignores expected disagg output. `session_create_replace` marks eligible row-store tables layered, either rewrites `table:` to `layered:` or appends layered block-manager config, then rejects indexes/log/import cases that are unsupported.

State and persistence behavior: Per-testcase sets `layered_uris` and `non_layered_uris` drive later URI rewriting. Persistent data may be stored through page-log/layered objects rather than normal `.wt` files; `tableExists` returns false and `initialFileName` returns `None` because local file mapping is not equivalent.

Dependencies and integration points: Uses `helper_disagg` storage discovery/output filters, `wthooks.DisaggParameters`, `WiredTigerTestCase.findExtension`, command-line var `page_log`, and hook platform API methods consumed by `wttest` and datasets.

Risks: URI tracking lives on the testcase rather than connection, so multiple homes/connections can confuse state. Config parsing is string/regex based and does not handle arbitrary nesting. Many unsupported features are skipped at runtime, so coverage is intentionally partial.

Test signals: Successful disagg runs show layered URI tracking, no unsupported-operation execution, expected verbose-output filtering, and normal suite assertions against layered data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_disagg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_nonstandalone.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_nonstandalone.py

Purpose: Marker hook for running the suite in a non-standalone WiredTiger build. It provides a hook name that tests can reference with `skip_for_hook` without changing core behavior.

Important APIs and types: `NonStandAloneHookCreator` extends `wthooks.WiredTigerHookCreator`, returns `wthooks.DefaultPlatformAPI`, has no hook registrations in `setup_hooks`, and `initialize` returns one creator.

Control flow: `run.py --hook nonstandalone` loads the module and installs the creator. The creator does not patch WiredTiger APIs and does not currently register broad skip categories. Individual tests are expected to opt out with decorators or hook-name checks.

State and persistence behavior: No test data, connection config, or persistent file behavior is changed. The only suite-visible state is that `WiredTigerTestCase.hook_names` contains `nonstandalone`.

Dependencies and integration points: Depends on `wthooks` and `wttest`; imported `unittest` and `parse_qsl` are unused. It integrates with `wttest.skip_for_hook`/`runningHook`.

Risks: The method is named `register_skipped_test` rather than the hook-manager-called `register_skipped_tests`, but because no broad skips are needed this has no practical effect unless future logic is added under the wrong name.

Test signals: Tests skipped by explicit nonstandalone decorators and otherwise unchanged suite behavior are the expected signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_nonstandalone.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_parallel_checkpoint.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_parallel_checkpoint.py

Purpose: Hook that enables WiredTiger parallel checkpoint threads for Python suite tests by appending `checkpoint_threads=<N>` to connection open configuration.

Important APIs and types: `_parse_threads` accepts no argument, a raw integer, or `threads=<N>` optionally wrapped in parentheses. `ParallelCheckpointHookCreator` stores the thread count, returns `DefaultPlatformAPI`, and registers a `wiredtiger_open` argument hook.

Control flow: The hook parses and validates a positive thread count, defaulting to four. On every `wiredtiger_open`, the argument hook converts the readonly args tuple to a list, checks whether the config already contains `checkpoint_threads=`, and appends the configured setting only when absent.

State and persistence behavior: It changes connection runtime behavior by enabling additional checkpoint worker threads. No files are written directly by the hook, but checkpoint scheduling can affect timing and persisted checkpoint state in test homes.

Dependencies and integration points: Uses the generic `wthooks.HOOK_ARGS` mechanism and `run.py --hook parallel_checkpoint[=...]`. It composes with the default platform API and other hooks that also modify open config.

Risks: String detection may miss semantically equivalent config forms or comments. More checkpoint concurrency can expose races or timing-sensitive tests. Invalid hook arguments abort hook initialization before tests run.

Test signals: Connections should open with parallel checkpoint configuration unless already explicit; tests should either pass under extra checkpoint concurrency or reveal checkpoint-thread-sensitive bugs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_parallel_checkpoint.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_rollback.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_rollback.py

Purpose: Fault-injection hook that randomly raises `WiredTigerRollbackError` from cursor operations inside transactions to test suite-level rollback retry and cleanup behavior.

Important APIs and types: Notification hooks `session_begin_transaction_notify`, `session_end_transaction_notify`, `session_open_cursor_notify`, `cursor_notify_for_rollback`, and `RollbackHookCreator`. The module also replaces `wiredtiger.Cursor.session` with a Python property returning the original session wrapper.

Control flow: Begin/commit/rollback notifications maintain `session.in_transaction`. Open-cursor notification records the creating session on the cursor. Cursor operation notifications for insert, modify, search, search_near, and update call `cursor_notify_for_rollback`; if the session is in a transaction and `do_retry()` matches the configured random rate, the hook prints a retry marker and raises `WiredTigerRollbackError`.

State and persistence behavior: Runtime state includes per-session `in_transaction`, per-cursor `_session_value`, a random generator, and an integer modulus derived from the fail rate. It does not intentionally persist data, but injected rollbacks force test retries and cleanup paths.

Dependencies and integration points: Integrates with `WiredTigerTestCase._callTestMethod`, which catches `WiredTigerRollbackError`, tears down, and restarts tests up to `rollbacks_allowed`.

Risks: Fail-rate `1.0` yields modulus one and always injects during eligible operations, while very small rates produce large moduli. The hook globally changes `Cursor.session`, which can affect other code in the process. Printed retry markers must be cleaned up by retry output handling.

Test signals: Expected rollback retries, cleaned stdout between retries, and final failures only after retry limits are exhausted validate the suite retry machinery.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_rollback.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_tiered.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_tiered.py

Purpose: Hook that runs ordinary row-store tests with tiered storage by injecting storage-source configuration, forcing tier flushes, adapting local-only creates, and skipping or stubbing unsupported tiered-table operations.

Important APIs and types: `wiredtiger_open_tiered`, helpers for readonly/failed/skipped test state, replacements for `Connection.close`, `Session.checkpoint`, `compact`, `create`, `open_cursor`, `salvage`, and `verify`, `TieredHookCreator`, argument parsing helpers, and `TieredPlatformAPI`.

Control flow: The open hook resolves the selected storage source from `helper_tiered`, rejects tests already using tiered/in-memory configs, creates the bucket directory, finds the extension, merges it into `extensions=[...]`, and appends `tiered_storage=(...)`. Checkpoint and close replacements force `flush_tier` unless readonly/failed/skipped. Create replacement marks non-table or column-store objects `tiered_storage=(name=none)`. Backup cursors and named checkpoints are skipped.

State and persistence behavior: Tests write both local WiredTiger state and tiered object files, with object names such as `<table>-0000000001.wtobj`. Platform API methods report tier-populate share/cache percentages, storage source name/config, and tiered filename existence. Dataset population uses those percentages to flush or reopen mid-fill.

Dependencies and integration points: Uses `helper_tiered.TieredConfigMixin`, `gen_tiered_storage_sources`, extension discovery, `WiredTigerTestCase` platform API delegation, and hook skip decorators.

Risks: Config parsing is regex/string based and handles only one level of parenthesized commas. Unsupported operations sometimes return success without doing work, so tests may pass with reduced semantic coverage. Object cleanup limitations make name-reuse tests problematic.

Test signals: Successful tiered runs show extension load, object creation, forced flush-tier checkpoints, correct `tableExists`/`initialFileName`, and expected skips for unsupported features.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_tiered.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_timestamp.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_timestamp.py

Purpose: Hook that injects automatic timestamp behavior into dataset-based tests by providing a timestamp generator and tracking explicit transaction boundaries.

Important APIs and types: Replacements `session_begin_transaction_replace`, `session_commit_transaction_replace`, `session_rollback_transaction_replace`, helper `make_dataset_names`, `TimestampHookCreator`, and `TimestampPlatformAPI`.

Control flow: On initialization, the hook discovers dataset class names from `wtdataset`. It skips tests whose module globals do not include a dataset type because the hook only affects dataset wrappers. `setup_hooks` replaces session transaction methods to call originals and maintain `session._has_transaction`. `TimestampPlatformAPI.setUp` creates a new `WiredTigerTimeStamp` for each testcase, which `wtdataset` uses for timestamped cursors.

State and persistence behavior: Per-testcase timestamp generator state increments as dataset cursor operations commit or timestamp transactions. Per-session `_has_transaction` prevents timestamped cursors from opening nested transactions when the test already has one active.

Dependencies and integration points: Depends on `wttimestamp`, `wtdataset`, hook platform API `getTimestamp`, and `wttest.prevent("timestamp")` for tests with custom timestamp logic.

Risks: Skip detection scans module globals and can miss indirect dataset use. Global replacement of transaction APIs affects all sessions in the process. If a transaction method raises before flag update, `_has_transaction` may become stale.

Test signals: Dataset tests should pass under automatic commit timestamps, custom timestamp tests should be skipped by `prevent`, and no nested-transaction errors should occur.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_timestamp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_timing_stress_log_conn_close.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_timing_stress_log_conn_close.py

Purpose: Hook that enables the `conn_close_stress_log_printf` timing stress setting across Python tests.

Important APIs and types: `wiredtiger_open_args` appends `timing_stress_for_test=[conn_close_stress_log_printf]` to connection config. `TimingStressLogCreator` extends `WiredTigerHookCreator`, returns `DefaultPlatformAPI`, and registers the open-argument hook. `initialize` returns the creator.

Control flow: For each `wiredtiger_open`, the hook converts args to a list, leaves single-argument calls and configs already containing `timing_stress_for_test` unchanged, and otherwise appends the stress config to the last argument.

State and persistence behavior: The hook changes runtime timing around connection close logging. It does not write files itself, but it can alter scheduling and log behavior during test teardown and close.

Dependencies and integration points: Uses `wthooks.HOOK_ARGS` and the WiredTiger test-only timing-stress configuration parser. Tests can detect active hook state via normal hook-name mechanisms.

Risks: The module comment invocation includes the `hook_` prefix, while `run.py --hook` normally expects names without that prefix. Like other config hooks, it relies on substring detection and appends comma-heavy config fragments.

Test signals: Connections should open with the timing stress enabled unless already configured, and suite tests should still close cleanly without unexpected log-output failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_timing_stress_log_conn_close.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/wthooks.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/wthooks.py

Purpose: Generic hook framework for the WiredTiger Python suite. It loads hook modules, monkey-patches WiredTiger module/class methods, chains argument/notification hooks, supports one replacement hook per method, and exposes platform APIs to the test harness.

Important APIs and types: Constants `HOOK_REPLACE`, `HOOK_NOTIFY`, `HOOK_ARGS`; `WiredTigerHookInfo`; `hooked_function`; `WiredTigerHookManager`; `HookCreatorProxy`; abstract `WiredTigerHookCreator`; `DisaggParameters`; `WiredTigerHookPlatformAPI`; `DefaultPlatformAPI`; and `MultiPlatformAPI`.

Control flow: `WiredTigerHookManager` parses hook names and optional args, imports `hook_<name>`, calls `initialize`, initializes each creator with proxies, calls `setup_hooks`, collects platform APIs, and appends the default API. `add_hook` installs a wrapper the first time a class/method is hooked, stores the original method, and appends arg/notify functions or records a single replacement. `hooked_function` runs arg hooks, calls replacement or original, then notifies hooks.

State and persistence behavior: Hook metadata is stored as new attributes on the WiredTiger module/classes, such as `_<method>_hooks` and `_<method>_orig`. This is process-global monkey-patched state and persists for the Python process. Platform APIs are chained in manager order and fall back to `DefaultPlatformAPI`.

Dependencies and integration points: Uses Python import machinery, `wiredtiger` bindings, `WiredTigerTestCase` for debug tty, and hook modules like tiered/disagg/timestamp. `wttest` calls `get_platform_api`, `register_skipped_tests`, `get_hook_names`, and `hooks_using`.

Risks: Only one replacement hook per method is allowed, so hook combinations can conflict. Method signature mismatches surface at runtime. Process-global patches are not undone between suites. `MultiPlatformAPI` uses first non-`NotImplementedError` result, making ordering significant.

Test signals: Hooks are validated indirectly by command-line hook runs, expected skip registration, modified connection configs, platform API overrides, and absence of duplicate replacement errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/wthooks.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/run.py -->
# sources/storage-engines/wiredtiger/test/suite/run.py

Purpose: Command-line runner for WiredTiger Python tests. It parses suite options, configures paths/build directory, loads hooks, discovers or selects tests/scenarios, applies batch/config/random filters, initializes `WiredTigerTestCase`, and executes via unittest or parallel concurrency.

Important APIs and types: Helpers include `usage`, `which`, `follow_symlinks`, `find`, `show_env`, `parse_int_list`, `verify_command_line_vars`, `restrictScenario`, `addScenarioTests`, `configRecord`, `configGet`, `configApplyInner`, `configApply`, `testsFromArg`, and `error`. Module globals include `wt_builddir` and `suitedir`.

Control flow: Startup sets Python paths through `test_util`, finds the build directory, and delays `wttest` import until ASAN env handling is complete. Main option parsing handles hooks, scenarios, batching, parallelism, dry-run, config files, seeds, ASAN restart, output handling, and command-line variables. It constructs a `WiredTigerHookManager`, calls `WiredTigerTestCase.globalSetup`, discovers tests or loads requested modules/groups, applies hook skip registration, random sampling, batch slicing, and finally calls `wttest.runsuite`.

State and persistence behavior: It may remove/recreate the suite test root via `globalSetup`, write config JSON files with `-C`, read skip lists/configs, set ASAN-related environment variables, and exec-restart Python for ASAN. It creates a random tiered object prefix for the run and passes seeds into suite random setup.

Dependencies and integration points: Integrates `test_util`, `testscenarios.generate_scenarios`, `discover`, `wthooks`, `wttest`, `unittest`, optional `concurrencytest` through `wttest.runsuite`, and extension/build-path discovery used by helpers.

Risks: Option parsing is manual and order-sensitive. ASAN restart depends on toolchain paths and environment. Scenario restrictions require a named test when `-s` is used. `testsFromArg` references `xrange`, which is only reached for numeric test ranges despite Python 3 enforcement.

Test signals: Exit status mirrors unittest success, dry-run prints selected tests, config-create output records suite hierarchy, batch/random filters select expected cases, and hook-driven skips/config changes appear in suite behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/run.py -->
