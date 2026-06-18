# subset-b-009058 research

Grouped research report for the WiredTiger cppsuite test entry points and csuite recovery, backup, random, direct-I/O, and lock tests in subset B. Each file section is delimited for deterministic source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/reverse_split.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/reverse_split.cpp

Purpose: defines the `test_harness::reverse_split` workload, a cppsuite test intended to exercise WiredTiger reverse split behavior by inserting data at the end of collections while removing/truncating ranges from the start. The test biases toward emptying low-key pages while high-key pages continue to grow, which is the page-tree shape that should drive reverse split paths during eviction.

Important APIs, types, and functions: the class inherits `test` from the cppsuite harness and overrides `remove_operation(thread_worker *)`. It uses `test_args`, `logger`, `random_generator`, `thread_worker`, `collection`, `scoped_cursor`, transaction helpers (`begin`, `commit`, `rollback`, `try_rollback`), and the worker `truncate` helper. The constructor injects `timing_stress_for_test=[split_3]` or `[split_4]` into `args.wt_open_config` when no user-supplied WiredTiger open configuration exists, then initializes operation tracking through the base harness.

Control flow: each remove worker asserts that there is one collection per thread, opens a cursor on the worker-specific collection, and loops while `tc->running()`. For each iteration it resets the cursor, begins a transaction, reads the first visible key, parses it as the minimum key ID, computes a random end key up to roughly 83 percent of the remaining key range, and attempts a truncate from the first key to that padded end key. Invalid or failed ranges are rolled back; successful truncates are committed and logged. The cursor is reset before sleeping and synchronizing with peer remove threads, which makes truncation bursts more aligned across workers.

State and persistence behavior: the persistent state is the WiredTiger table data managed by the cppsuite database model. The workload mutates collections transactionally by truncating key ranges. It also mutates the process-level test argument object by appending stress timing configuration before the connection opens. Cursor reset is used to avoid pinning content across sleep/sync windows.

Dependencies and integration points: integrated through `run.cpp`, which includes this `.cpp` and dispatches `reverse_split(args).run()`. It depends on the cppsuite framework's collection-per-thread setup, key padding convention, operation tracker, and worker synchronization primitives. It also depends on numeric string keys; `std::stoi` on the cursor key must match the harness key format.

Risks: if the harness key format changes away from numeric padded strings, key parsing will fail or truncate the wrong range. The calculation `min_key_id + ((key_count - min_key_id) / 1.2)` assumes key IDs and collection key counts remain comparable after truncates. Very small remaining ranges cause repeated rollback/no-op iterations. The test is intentionally timing-sensitive because synchronized truncation is used to increase reverse split pressure.

Test signals: useful signals are warning logs about injected split timing stress, trace/info logs of committed truncation sizes, absence of transaction/assert failures, and coverage in eviction/reverse split diagnostics under the cppsuite `reverse_split` target.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/reverse_split.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/run.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/run.cpp

Purpose: implements the main executable for the cppsuite test framework. It parses command-line options, reads framework configuration strings, lists available tests, and dispatches named tests such as `reverse_split`, `operations_test`, `cache_resize`, bounded cursor tests, background compaction, and benchmark tests.

Important APIs, types, and functions: `parse_configuration_from_file` removes whitespace and comment lines before concatenating a config file into a single framework configuration string. `print_help` renders the CLI. `run_test` builds `test_harness::test_args` and dispatches by test name to concrete test classes included directly into this translation unit. `get_default_config_path` maps a test name to `configs/<test>_default.txt`. `main` uses `testutil_set_progname`, `logger::trace_level`, `connection_manager::instance().close()`, and the C++ harness classes included at the top of the file.

Control flow: `main` scans arguments manually. `-C` appends additional WiredTiger open configuration, `-c` supplies a framework configuration string, `-f` reads configuration from a file, `-H` sets home, `-l` sets trace level, `--list` prints all known tests, and `-t` chooses a single test. With no `-t`, it iterates `all_tests`, loading either the shared config file, each test's default config, or the `-c` string, skips `api_instruction_count_benchmarks` because it requires elevated permissions, runs each test, closes the singleton connection manager between tests, and stops at the first error. With `-t`, it validates membership and runs only that test.

State and persistence behavior: runtime state is mostly process-local CLI/config state plus logger verbosity. Each dispatched test owns its own WiredTiger home and workload state through the harness. When running all tests, explicit `connection_manager::close()` prevents singleton connection state from leaking between tests.

Dependencies and integration points: this file is the cppsuite integration hub; it includes individual test implementation `.cpp` files directly and must keep `all_tests`, `--list`, and `run_test` dispatch in sync. It depends on `test_util.h` for program-name/error handling and on default config files under `configs/`.

Risks: direct `.cpp` inclusion can hide ODR or dependency problems until this single target is built. The `-c`/`-f` error messages say `-C` in places where the conflicting option is framework config, which can confuse users. `parse_configuration_from_file` indexes `line[0]` before checking `line.empty()`, so an empty physical line can be undefined behavior after whitespace removal. Manual option parsing is flagged by the in-file FIXME.

Test signals: `./run --list` should enumerate every dispatchable test; `./run -t <name>` should load the default config and run exactly one test; all-test mode should close and reopen cleanly between tests and skip only the privileged instruction-count benchmark.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/run.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/test_disagg_failover_perf.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/test_disagg_failover_perf.cpp

Purpose: standalone cppsuite-style performance test that measures WiredTiger disaggregated storage failover/step-up time on a running system. It creates or copies a disaggregated database, starts as a follower, picks up the latest PALite checkpoint, optionally warms cache, performs append or update ingestion, reconfigures to leader, and writes the `disagg_step_up_time` statistic to a perf JSON file.

Important APIs, types, and functions: `options` stores workload shape, collection count, cache size, key/value sizing, ingest target, warm cache percent, verbosity, and load-copy/skip flags. `workload_type` selects append or updates. `initialize` creates the database model. `parse_options` uses `__wt_getopt`. `update_global_timestamps` calls `connection_manager::set_timestamp`. `populate`, `cache_warming`, `append`, `update`, `crud_worker`, and `crud_operations` drive data creation and mutation. `wt_disagg_pick_up_latest_checkpoint` obtains `WT_PAGE_LOG` `palite`, calls `pl_get_complete_checkpoint`, and reconfigures the connection with returned checkpoint metadata. `metrics_monitor` and `metrics_writer` export the statistic.

Control flow: `main` parses options, removes the home path, initializes a `database` model, builds shared connection and extension configuration, then either copies `home.back` and registers existing collections or opens as a disaggregated leader and populates timestamped collections. It closes the leader, optionally writes a backup copy, reopens as a disaggregated follower with statistics and PALite, refreshes `ts` from the stable timestamp if using existing data, picks up the latest checkpoint, optionally warms cache by scanning a prefix of records, executes the requested ingest workload, reconfigures to leader, sets the stable timestamp to the picked-up checkpoint timestamp, waits for FTDC/stat flush, reads `WT_STAT_CONN_DISAGG_STEP_UP_TIME`, writes the perf file, and deletes the model.

State and persistence behavior: creates or copies `opt.home_path` and optionally `opt.home_path.back`. It persists WiredTiger collections, PALite page-log state, checkpoints, timestamps, statistics logs, and a JSON perf result named from the program. The global `ts` monotonically advances through populate and workload operations, and `database_model` tracks collection counts for generated keys.

Dependencies and integration points: depends on the cppsuite storage abstractions, `crud`, `transaction`, `timestamp_manager`, `connection_manager`, PALite extension path `../../ext/page_log/palite/libwiredtiger_palite.so`, `WT_PAGE_LOG` disaggregated APIs, WiredTiger statistics, and the perf metrics writer component. It is not dispatched by `run.cpp`; it is a separate test executable.

Risks: extension paths are relative to the test runtime layout. The update workload assumes every generated key exists and that `collection::get_key_count` stays accurate across appends. `strndup`/manual free around checkpoint metadata must stay paired with PALite allocation semantics. The shared global `ts` and model pointer make the program single-run/single-process oriented. The test deletes `home_path` at startup even when `-L` then expects `home_path.back` to exist.

Test signals: successful output includes population/copy progress, follower pickup of a complete checkpoint, optional cache warming, ingest completion, leader reconfiguration, statistic retrieval, and a perf JSON containing `disagg_step_up_time`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/test_disagg_failover_perf.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/test_live_restore.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/test_live_restore.cpp

Purpose: standalone live restore stress test. It creates a source WiredTiger database, copies it into a live-restore source directory, then repeatedly opens a target home with `live_restore=(enabled=true,path=...)` while random CRUD, checkpoints, compaction/truncation, reopens, optional crash, and recovery modes run concurrently with background file migration.

Important APIs, types, and functions: the local `database_model` tracks collection URIs and can add new or existing collections, including nested subdirectory paths. Workload helpers include `read`, `trigger_fs_truncate`, `insert`, `update`, `remove`, `write`, `create_collection`, `reopen_conn`, and `do_random_crud`. `configure_database` scans `metadata:` after recovery to rebuild the model. `take_backup_and_delete_original` uses a `backup:` cursor and file copies, with special handling for journal log files and subdirectory tables. `run_restore` opens live restore, waits for `WT_STAT_CONN_LIVE_RESTORE_STATE == WT_LIVE_RESTORE_COMPLETE`, deletes the source directory, and continues CRUD to verify no source reads remain. `create_db` builds the initial database.

Control flow: `main` parses options for iterations, background thread count, collection cap, directory-per-db simulation, death mode, recovery, operation count, WT verbose level, log level, and home path. In normal mode it deletes old home/source paths, creates a database, backs it up into `WT_LIVE_RESTORE_SOURCE`, and deletes the original. Each iteration runs live restore, optionally kills itself on a selected iteration, then turns the restored home into the next source backup. Recovery mode skips directory setup, rebuilds model state from metadata, and runs a single iteration.

State and persistence behavior: uses `DEFAULT_DIR` as target home and `WT_LIVE_RESTORE_SOURCE` as backing source unless overridden. It creates/deletes homes and source directories, copies log files under `journal`, optionally creates nested table paths under `SUB_DIR/SUB_DIR`, enables statistics/logging, writes many large random values, and uses backup copies to chain iterations. Source deletion after restore completion is an intentional persistence check.

Dependencies and integration points: depends on WiredTiger live restore configuration, connection/session manager, cppsuite scoped sessions/cursors, `test_util` filesystem helpers, metadata and backup cursors, live restore connection statistics, logging, and POSIX `SIGKILL` for death mode.

Risks: the `remove` helper appears to call `cursor->next(ran_cursor.get())` instead of invoking `next` on `ran_cursor`; if enabled, that mismatch would likely break random removals. Random CRUD plus connection reopens makes failures timing-dependent. Deleting the source directory assumes the live restore state statistic is authoritative. Recovery mode supports only one iteration. File-copy logic has hand-coded journal and subdirectory cases that must track WiredTiger filename conventions.

Test signals: live restore completion is detected by `WT_LIVE_RESTORE_COMPLETE`; deleting the source followed by more CRUD should not crash; recovery mode should repopulate collection metadata; optional death-mode runs should be restartable with `-r`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/test_live_restore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/test_template.cpp -->
# sources/storage-engines/wiredtiger/test/cppsuite/tests/test_template.cpp

Purpose: minimal cppsuite template showing how to define a new harness test and custom operation tracker. It intentionally overrides all major workload hooks with no-op logging so developers can copy and replace pieces when creating a real test.

Important APIs, types, and functions: `operation_tracker_template` derives from `operation_tracker` and overrides `set_tracking_cursor`, currently delegating to the base implementation. `test_template` derives from `test`, initializes the operation tracker with `OPERATION_TRACKER`, compression, and timestamp manager configuration, overrides `run`, `populate`, operation hooks (`background_compact_operation`, `checkpoint_operation`, `custom_operation`, `insert_operation`, `read_operation`, `remove_operation`, `update_operation`), and `validate`.

Control flow: constructing `test_template` initializes tracking. `run` delegates to `test::run`, so the standard harness lifecycle still executes. Every operation hook logs a warning and performs no database work; validation also logs only.

State and persistence behavior: no application data is created by the template itself. The only state is framework initialization and any base harness scaffolding invoked by `test::run`. The custom tracker would control tracking table contents if changed.

Dependencies and integration points: included and dispatched by `run.cpp` as `test_template`. It depends on cppsuite constants, logger, configuration, timestamp manager, and operation tracking APIs.

Risks: because it logs no-op warnings but still runs the base harness, using the template unchanged can produce a passing test that does not validate behavior. Any copied test must replace both workload and validation methods to become meaningful.

Test signals: useful only as a compile/lifecycle smoke test. Expected runtime output is a sequence of warnings stating that populate, operations, and validation did nothing.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cppsuite/tests/test_template.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/csuite/CMakeLists.txt

Purpose: declares the WiredTiger `test/csuite` C test targets through the repository's `define_c_test` macro. It maps each csuite subdirectory to executable source files, arguments, smoke scripts, platform dependencies, additional files, labels, flags, and in one case C++ linker language.

Important APIs, types, and functions: the repeated build API is `define_c_test(TARGET ... SOURCES ... DIR_NAME ... EXEC_SCRIPT ... ARGUMENTS ... ADDITIONAL_FILES ... DEPENDS ... LABEL ... FLAGS ...)`. Targets in this subset include `test_normalized_pos`, `test_config`, `test_incr_backup`, `test_random`, `test_random_abort`, `test_random_directio`, `test_random_session`, and `test_rwlock`. The file also defines many other csuite targets such as timestamp, checkpoint, checksum, compact, schema, and disaggregated tests.

Control flow: CMake evaluates each `define_c_test` block during configure/generate. Blocks can attach POSIX gating through `DEPENDS "WT_POSIX"`, mark long-running or disaggregated tests via `LABEL`, pass generated target-file paths using generator expressions, and install/copy smoke scripts or companion scripts. The final block for `test_wt16990_disagg_checkpoint_panic` sets `LINKER_LANGUAGE CXX` when the target exists so sanitizer and extension runtimes link correctly.

State and persistence behavior: no runtime state is written by the CMake file itself, but it controls per-test build directories, copied scripts, `WT_HOME` argument locations, and whether targets enter CTest. The runtime tests create and remove their own WiredTiger homes under generated binary directories.

Dependencies and integration points: integrates csuite with the top-level WiredTiger CMake harness and `define_c_test`. It depends on target names matching source directories and smoke script paths. POSIX-dependent tests rely on `WT_POSIX`; direct-I/O, random abort, backup, and shell smoke scripts are gated accordingly.

Risks: target/source/script naming drift can silently break CTest registration. Long-running labels must stay accurate for sanitizer/buildbot scheduling. `test_random_directio` compiles both `main.c` and `util.c`; omitting helper sources would link-fail. Additional smoke scripts, such as LazyFS variants, must be listed to be available in build directories.

Test signals: CMake generation should create all requested targets, CTest should attach correct scripts/arguments/labels, and POSIX-gated targets should be omitted or disabled on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/config/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/config/main.c

Purpose: exhaustive csuite test for WiredTiger precompiled configuration strings for APIs that support `WT_CONNECTION::compile_configuration`. It validates rejection of malformed configs, parameter binding, use of compiled configs, valid/invalid key values, and the verbose reconstruction output for `WT_SESSION.begin_transaction` and `WT_SESSION.reconfigure`.

Important APIs, types, and functions: `PARSE_STATE` records verbose callback state, `CUSTOM_EVENT_HANDLER` embeds `WT_EVENT_HANDLER`, and `KEY_VALUES` describes configuration keys with valid/invalid values and nested subcategories. The key lists cover begin-transaction settings and session reconfigure settings. `COPY_MESSAGE_CONTENT` extracts quoted content from verbose messages. `check_configuration_result` and `check_single_result_against_inputs` parse reconstructed compiled output with `wiredtiger_config_parser_open`. `handle_wiredtiger_message` consumes verbose `configuration:2` messages. `check_compiling_configurations` drives all compile/bind/use/error checks.

Control flow: `main` installs a custom event handler, parses standard test options, recreates the home, opens WiredTiger with `verbose=(configuration:2)`, and opens a session. It then calls `check_compiling_configurations` for `WT_SESSION.begin_transaction` expecting 46 successful reconstruction callbacks and for `WT_SESSION.reconfigure` expecting 89. Each check first confirms generic bad config failures and unsupported method failure, then compiles `isolation=%s`, verifies unbound use fails, binds `snapshot`, uses the compiled configuration on the matching API, compiles an empty string, rejects compiling an already compiled string, tests every invalid value, and then tests every valid value while the message callback validates the reconstructed config.

State and persistence behavior: creates a temporary WiredTiger home with statistics/statistics_log enabled, but does not create application tables. Most state is in the custom event handler and parser allocations, which are freed between compilations.

Dependencies and integration points: depends on the public configuration compiler, config parser, event handler callbacks, session transaction/reconfigure APIs, `test_util` option parsing, and verbose message text containing `for method:`, `input config:`, and `reconstructed config:`.

Risks: the test is intentionally coupled to exact verbose output structure and exact successful-output counts; legitimate changes to verbose messages or supported keys require updating expected counts and key lists. `reconfigure_kv` contains a duplicated `debug` entry, which contributes to the expected output count. Nested subcategory validation supports only one nested level.

Test signals: successful run prints the checked output counts for both methods and exits cleanly. Any parser, compiler, verbose callback, or API use regression should trip `testutil_assert`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/config/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/incr_backup/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/incr_backup/main.c

Purpose: randomized incremental backup correctness test. It creates and mutates many tables with predictable per-table histories, alternates full and incremental backups, verifies backup contents after each iteration, and records seeds so failures can be reproduced.

Important APIs, types, and functions: `TABLE` tracks one table slot, table name, generation index, change count, random state, and max value size. `TABLE_INFO` tracks the table array, tables in use, full backup number, and incremental backup number. `OPERATION_TYPE` defines insert, modify, remove, and update phases. `key_value` deterministically maps a table change count to an expected key/value and operation. `table_changes`, `create_table`, and `drop_table` mutate live tables. `base_backup` calls `testutil_backup_create_full`; `incr_backup` calls `testutil_backup_create_incremental`; `check_backup` opens a copied backup and calls `check_table` for each live table. `run_test` orchestrates random schema/data/checkpoint/reopen/backup cycles.

Control flow: `main` parses home, preserve, seed, and verbosity. Without a seed it runs two fixed seeds plus one random seed; with `-S` it runs that seed. `run_test` creates an isolated working directory and `WT_HOME`, chooses max value sizes, log file sizes, table count, per-table random seeds, and a checkpoint cadence. Across ten iterations it randomly creates/drops table slots, mutates live tables, checkpoints periodically, sometimes closes/reopens and copies the source bitmap while closed, takes a full backup on iteration 0, then either a new full backup or an incremental backup on later iterations, verifies the resulting backup copy, and prunes old backups.

State and persistence behavior: creates `WT_TEST.incr_backup` by default, a nested `WT_HOME`, backup directories (`BACKUP_BASE`, `CHECK_BASE` via testutil helpers), optional preserved artifacts, log files with random `file_max`, and incremental backup metadata. Table data cycles through predictable insert/update/modify/remove phases so the expected final state can be reconstructed from `change_count`.

Dependencies and integration points: depends on WiredTiger logging, checkpointing, table create/drop, modify API (`wiredtiger_calc_modify`), backup cursors/helpers from `test_util.h`, random APIs, and POSIX directory handling. It is registered by `test_incr_backup` and normally launched through `smoke.sh`.

Risks: the test is random and storage-heavy; failures need the printed seed and possibly preserve mode. Incremental backup correctness depends on backup helper semantics and bitmap/granularity behavior. The TODO notes preserve artifacts can nest under `WT_TEST.incr_backup/WT_TEST.incr_backup...`. Very small or zero max value sizes are possible and intentionally exercised.

Test signals: every backup verification must open the copied backup and match all expected records. The smoke script runs `-v 3`, and final output includes `Success.` and total copied backup ranges with granularity/allocation information.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/incr_backup/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/incr_backup/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/incr_backup/smoke.sh

Purpose: shell smoke wrapper for `test_incr_backup` as part of `make check`/CTest.

Important APIs, types, and functions: the script uses POSIX `sh`, `set -e`, optional first argument for the test binary, `binary_dir=${binary_dir:-\`dirname $0\`}`, `TEST_WRAPPER`, and executes the resolved binary with `-v 3`.

Control flow: if `$1` is non-empty, it is treated as the binary path. Otherwise the script assumes it has been copied to the build directory and resolves `test_incr_backup` beside itself. It then runs `$TEST_WRAPPER $test_bin -v 3`; `set -e` makes any nonzero exit fail the smoke test.

State and persistence behavior: the script itself writes no files, but the test binary creates and removes or preserves `WT_TEST.incr_backup` and backup artifacts depending on binary options. It raises verbosity enough to expose backup progress.

Dependencies and integration points: copied by `CMakeLists.txt` through `define_c_test(EXEC_SCRIPT ...)`, depends on `TEST_WRAPPER` when supplied by the harness, and assumes build-directory layout for default binary discovery.

Risks: running the source-tree script directly without passing a binary can resolve the wrong path because the fallback assumes build-directory placement. Backtick command substitution is portable but old style.

Test signals: successful smoke execution is simply a zero exit from the verbose incremental backup randomized test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/incr_backup/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/normalized_pos/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/normalized_pos/main.c

Purpose: white-box correctness test for WiredTiger normalized page positions (`npos`). It verifies that pages can be traversed in normalized-position order and that an `npos` computed from a page maps back to the expected page for both eviction and read lookup paths.

Important APIs, types, and functions: the test includes `wt_internal.h` and uses internal types `WT_SESSION_IMPL`, `WT_CURSOR_BTREE`, `WT_DATA_HANDLE`, and `WT_REF`. `create_btree` creates `table:normalized_pos` with small 1KB page sizing and inserts 100,000 fixed-size values. `test_normalized_pos` accepts either `__wt_page_from_npos_for_eviction` or `__wt_page_from_npos_for_read`, calls `__wt_page_npos`, releases refs with `__wt_page_release`, and uses `WT_WITH_DHANDLE`. `run` executes both in-memory and on-disk variants.

Control flow: `run` creates a working home, opens WiredTiger either in-memory with 1GB cache or on-disk with 1MB cache, builds the btree, then runs the normalized-position test for eviction and read. `test_normalized_pos` first searches all keys to stabilize the tree, walks forward from `npos=0` and backward from `npos=1` using page-from-npos callbacks, checks monotonic npos movement, optionally checks exact page count and no duplicate refs in memory, then searches every key, computes the page's midpoint npos and optional path string, checks monotonicity across keys, maps the npos back to a page, and verifies exact ref equality in memory.

State and persistence behavior: creates and deletes `WT_TEST.normalized_pos`. In-memory mode keeps the page shape simple and stable; on-disk mode permits less exact page counts because disk layout can pack pages differently. The test manipulates hazard references and releases them explicitly.

Dependencies and integration points: depends on internal WiredTiger page tree functions and structures, not public API stability. Registered as `test_normalized_pos` and normally launched through `normalized_pos/smoke.sh`.

Risks: tightly coupled to internal Btree/page-ref behavior. The comments note the one-key-per-page expectation is not always exact. Any change in page split/layout, hazard pointer discipline, or normalized-position algorithm may require adjusted assertions. Because it uses internal headers, it is not a portable external test.

Test signals: in-memory runs should traverse exactly `NUM_KEYS` pages forward and backward and map every key page back exactly. On-disk runs should preserve monotonic order and forward/backward count equality for read lookup where asserted.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/normalized_pos/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/normalized_pos/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/normalized_pos/smoke.sh

Purpose: shell smoke wrapper for the normalized position csuite test.

Important APIs, types, and functions: uses POSIX `sh`, `set -e`, optional binary path argument, `binary_dir` fallback to `dirname $0`, and `TEST_WRAPPER`.

Control flow: resolves the binary either from `$1` or `$binary_dir/normalized_pos`, then runs it under `$TEST_WRAPPER` with no additional options. Any nonzero exit fails because `set -e` is active.

State and persistence behavior: the wrapper writes no state. The binary creates and removes `WT_TEST.normalized_pos`.

Dependencies and integration points: registered by `CMakeLists.txt` as the `EXEC_SCRIPT` for `test_normalized_pos`. The default binary name in the script is `normalized_pos`, so build-system target/binary naming must match the copied script environment.

Risks: direct source-tree execution without a binary argument can resolve an invalid binary path. The wrapper does not pass `-v`, so detailed npos trace output is disabled in normal smoke runs.

Test signals: zero exit from the normalized-position binary validates both in-memory and on-disk internal npos paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/normalized_pos/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/random/main.c

Purpose: deterministic regression test for WiredTiger's default random number generator sequence. It verifies that values at powers-of-two call counts match a fixed expected array.

Important APIs, types, and functions: `EXPECTED_RANDOM` stores 35 expected `uint32_t` values. `test_random` initializes `WT_RAND_STATE` with `__wt_random_init_default`, repeatedly calls `__wt_random`, and checks the generated value whenever the call count equals `1 << i`. `usage` and `main` handle the optional `-v` flag.

Control flow: `main` sets the program name, skips under `ENABLE_ANTITHESIS`, parses `-v`, rejects extra arguments, and calls `test_random`. In verbose mode, the test prints the index, count, and random value at each checked power of two.

State and persistence behavior: no database is opened and no files are written. The only state is the local RNG state and loop counters.

Dependencies and integration points: depends on WiredTiger internal random APIs exposed through `test_util.h`. This test is a compatibility guard for deterministic PRNG behavior used by other tests and reproducibility.

Risks: intentional changes to the RNG algorithm or default seed sequence require updating `EXPECTED_RANDOM` and may affect reproducibility of many seeded tests. The loop count grows to the last power-of-two checkpoint, so adding many more expected values can increase runtime sharply.

Test signals: zero exit means every checked power-of-two output matched. Verbose output is useful when regenerating the expected sequence after an intentional algorithm change.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_abort/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/random_abort/main.c

Purpose: crash/recovery stress test that forks a writer process, lets multiple threads write row-store and column-store tables plus sidecar record logs, kills the child with `SIGKILL`, runs WiredTiger recovery, and verifies that recovered records are consistent with the durable prefix described by the sidecar files.

Important APIs, types, and functions: global options control compatibility mode, compaction, in-memory logging, and LazyFS. `thread_run` writes records forever, alternating row/column tables by thread ID, performing inserts, removes, and modify/update operations, and logging inserted/deleted/modified keys to per-thread files under `RECORDS_DIR`. `fill_db` creates `table:main` and `table:col_main`, opens the connection with log/transaction_sync config, and starts writer threads. `recover_and_verify` reopens with recovery config, reads sidecar files, and validates key presence/absence/value contents. `handler` cleans up LazyFS if the child exits unexpectedly.

Control flow: `main` parses options (`-C`, `-c`, `-h`, `-l`, `-m`, `-p`, `-T`, `-t`, `-v`), chooses random or fixed thread counts and timeout, creates the work directories and LazyFS if enabled, forks the child to run `fill_db`, waits until every worker has created its three record files, sleeps the timeout, kills the child, copies data for debugging, optionally clears LazyFS cache, changes into the home, and runs recovery verification. Verify-only mode skips the fork and requires an explicit thread count.

State and persistence behavior: creates `WT_TEST.random-abort` or `WT_TEST.random-abort-lazyfs`, a nested `WT_HOME`, record files for inserts/deletes/modifies, debug data copies, optional LazyFS backing/cache state, log files, and row/column tables. It cleans artifacts unless preservation or failure prevents cleanup.

Dependencies and integration points: depends on POSIX fork/signals/wait, WiredTiger logging/recovery, transaction sync variants, `wiredtiger_calc_modify`, column-store record numbering, LazyFS test utilities, `testutil_copy_data`, and smoke scripts that run disk, in-memory, compatibility, and LazyFS variants.

Risks: sidecar files can contain partial lines after `SIGKILL`; verification explicitly treats malformed/partial tails as EOF. The test assumes recovered durable data forms a prefix per thread; any later existing key after a missing key is fatal. LazyFS mode changes durability expectations by clearing the cache. Workload threads never stop voluntarily, so process control must be correct.

Test signals: successful recovery prints the number of verified records and exits zero. Non-in-memory runs fail if records that should be durable are absent or values mismatch. Smoke scripts exercise fixed five-thread, fixed-time variants across compatibility, in-memory, and LazyFS modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_abort/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_abort/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/random_abort/smoke.sh

Purpose: standard smoke wrapper for `test_random_abort`.

Important APIs, types, and functions: uses POSIX `sh`, `set -e`, optional binary path argument, `binary_dir` fallback, `TEST_WRAPPER`, and fixed test options.

Control flow: resolves `test_random_abort`, then runs four variants: default logged disk mode, in-memory logging (`-m`), compatibility mode (`-C`), and compatibility plus in-memory logging. Every variant uses `-t 10 -T 5` to bound runtime and thread count.

State and persistence behavior: the wrapper writes no direct state. Each binary invocation creates and cleans its own random-abort work directory unless failure/preserve options intervene.

Dependencies and integration points: registered as `EXEC_SCRIPT` for `test_random_abort`; `CMakeLists.txt` also lists the LazyFS companion script as an additional file. Depends on `TEST_WRAPPER` and POSIX shell behavior.

Risks: four sequential crash/recovery runs can be expensive on slow machines. The script does not run compaction or LazyFS variants; those are covered separately.

Test signals: zero exit from all four fixed variants is the smoke signal for recovery under default, in-memory log buffering, compatibility, and combined modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_abort/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_abort/smoke_lazyfs.sh -->
# sources/storage-engines/wiredtiger/test/csuite/random_abort/smoke_lazyfs.sh

Purpose: LazyFS-specific smoke wrapper for `test_random_abort`.

Important APIs, types, and functions: uses POSIX `sh`, `set -e`, optional binary argument, build-directory fallback, `TEST_WRAPPER`, and the binary's `-l` LazyFS flag.

Control flow: resolves `test_random_abort`, then runs LazyFS mode with `-l -t 30 -T 5` and LazyFS plus compatibility mode with `-l -C -t 30 -T 5`.

State and persistence behavior: no direct script state. The binary creates the LazyFS work directory, sets up/cleans LazyFS, and clears the LazyFS cache before recovery verification.

Dependencies and integration points: listed as `ADDITIONAL_FILES` for the random-abort CMake target. It assumes the environment has LazyFS support; the binary can implicitly enable LazyFS as well.

Risks: longer timeout than the standard smoke script increases runtime. LazyFS availability and mount/setup behavior are environment-sensitive.

Test signals: zero exit from both LazyFS variants validates recovery under simulated lost write-cache behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_abort/smoke_lazyfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_directio/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/random_directio/main.c

Purpose: direct-I/O crash simulation test. A child writer process continuously mutates tables while the parent periodically stops it, copies the database home using direct I/O, opens the copy with recovery, verifies table consistency, resumes the child, and repeats. This approximates on-disk state after a crash without relying on buffered filesystem reads.

Important APIs, types, and functions: `WT_THREAD_DATA` stores per-thread connection, buffer, data size, ID, RNG, and schema flags. `large_buf`, `gen_kv`, `gen_table_name`, and `gen_updated_value` generate deterministic keys/values/schema table names. `schema_operation` creates/inserts/updates/drops per-thread tables during selected ID windows. `thread_run` writes `table:main` and `table:rev` transactionally and optionally integrates schema operations. `thread_ckpt_run` checkpoints and flushes tiered storage. `create_db`, `fill_db`, `check_kv`, `check_schema`, and `check_db` implement setup, child workload, and recovered-copy validation. `handler`, `kill_child`, and `die` handle abnormal child exits.

Control flow: `main` verifies `O_DIRECT` support, parses options for checkpointing, tiered storage, data size, schema frequency, home, copy interval, sync method, cycle count, populate/verify/preserve, schema flags, thread count, and initial timeout. In normal mode it creates the home, optional tier bucket, randomizes thread count/timeouts when requested, creates base tables, forks the child, sleeps, then for each cycle sends `SIGSTOP`, calls `check_db` with direct I/O copy, sends `SIGCONT`, and finally kills the child. Verify-only mode checks an existing home without direct I/O.

State and persistence behavior: creates `WT_TEST.random-directio`, optional `bucket`, base tables `table:main` and `table:rev`, optional schema tables `table:A<id>-<thread>`, debug/check/save copies (`.DEBUG`, `.CHECK`, `.SAVE`), logs, checkpoints, and tiered-storage objects. Validation scans the recovered copy from near the last complete ID neighborhood and checks both main and reverse tables plus schema metadata.

Dependencies and integration points: depends on POSIX signals/fork/wait, `O_DIRECT`, helper `copy_directory` from `util.c`, WiredTiger logging/recovery/transactions/checkpoints/tiered storage, `dir_store` extension paths, testutil option parsing, and CMake linking `random_directio/util.c`.

Risks: this is highly timing- and filesystem-dependent. The direct-I/O copy can observe files disappearing during schema drops; helper logic tolerates `ENOENT` on source open. `check_kv` currently calls `cursor->search` twice, which is redundant but should be harmless. Tiered storage requires checkpoint mode. Many stronger integrated schema checks are commented out in the smoke script as not reliably passing.

Test signals: each cycle should copy, recover, scan to the last consistent ID, validate reverse-table pairs and schema expectations, then print `SUCCESS`. The smoke script runs a bounded five-thread, five-second default plus create/drop schema variant.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_directio/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_directio/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/random_directio/smoke.sh

Purpose: smoke wrapper for the direct-I/O crash simulation test.

Important APIs, types, and functions: uses POSIX `sh`, `set -e`, `binary_dir` fallback, optional first-argument binary path, `TEST_WRAPPER`, `TEST_THREADS`, `TEST_METHODS`, and constructed `RUN_TEST` commands.

Control flow: resolves `test_random_directio`, sets the smoke matrix to one thread-count value (`5`) and one transaction sync method (`none`), then runs a default fixed-time test and a schema create/drop verbose variant with `-f 20 -S create,drop,verbose`. More exhaustive thread/method and integrated schema variants are present as commented commands.

State and persistence behavior: the wrapper writes no direct state. Each binary run creates direct-I/O work directories and recovered copies, cleaning on success unless preservation options are added manually.

Dependencies and integration points: registered as `EXEC_SCRIPT` for `test_random_directio`; depends on `TEST_WRAPPER`, the built binary, Linux/direct-I/O support, and CMake copying the script beside the binary or passing the binary path.

Risks: the smoke matrix is intentionally reduced; it does not cover `fsync`, `dsync`, tiered storage, or the stronger integrated schema checks. The direct-I/O binary may skip if `O_DIRECT` is unavailable.

Test signals: both smoke invocations must exit zero. Failure in either default or create/drop schema mode indicates crash-copy recovery inconsistency or environment incompatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_directio/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_directio/util.c -->
# sources/storage-engines/wiredtiger/test/csuite/random_directio/util.c

Purpose: helper implementation for recursively copying a database directory, optionally using direct I/O for source reads, so `random_directio/main.c` can verify what is actually on disk.

Important APIs, types, and functions: defines `ALIGN_UP`, `ALIGN_DOWN`, `BUFFER_ALIGNMENT_DEFAULT`, `COPY_BUF_SIZE`, internal `copy_directory_int`, and exported `copy_directory`. It uses POSIX directory APIs (`opendir`, `readdir`, `closedir`), filesystem calls (`mkdir`, `open`, `fstat`, `read`, `write`, `close`), `O_DIRECT` when requested, and `testutil_remove` for destination cleanup.

Control flow: `copy_directory` removes the destination tree and calls `copy_directory_int`. The recursive helper creates the destination directory, iterates entries, skips `.`/`..`, recurses for directories, opens source files with `O_DIRECT` if requested, creates destination files normally, aligns the reusable buffer and read sizes to the source block size for direct I/O, copies file contents in chunks, and closes descriptors. If a source file disappears with `ENOENT`, it logs and skips it because WiredTiger drop can unlink before directory sync while the child is stopped.

State and persistence behavior: writes a complete destination directory tree, potentially omitting files that vanished during a concurrent drop. It allocates and frees a copy buffer per recursive call. Destination file permissions are created as `0666` subject to umask.

Dependencies and integration points: declared in `util.h` and linked into `test_random_directio`. It depends on `test_util.h`, platform `O_DIRECT`, `dirent.d_type` reporting directories, and WiredTiger utility macros such as `WT_MAX` and `WT_MIN`.

Risks: `dirent.d_type` can be `DT_UNKNOWN` on some filesystems, which this code does not stat-and-classify. Direct-I/O assumptions require aligned buffers and read sizes; the code asserts consistent block size after first allocation. It does not preserve metadata such as modes, ownership, or timestamps beyond creating files. Concurrent directory changes other than `ENOENT` can still assert.

Test signals: random-directio cycles succeeding under direct I/O validate this helper. The printed `COPY_DIR` `ENOENT` messages are expected only for files dropped during copy.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_directio/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_directio/util.h -->
# sources/storage-engines/wiredtiger/test/csuite/random_directio/util.h

Purpose: small header exposing the direct-I/O directory copy helper used by `random_directio/main.c`.

Important APIs, types, and functions: contains `#pragma once` and the declaration `extern void copy_directory(const char *, const char *, bool);`.

Control flow: no executable control flow; it provides the function prototype so the main test can call the helper implemented in `util.c`.

State and persistence behavior: no state is stored in the header. The declared function writes destination directory trees at runtime.

Dependencies and integration points: included by both `main.c` and `util.c`; requires `bool` to be available from included headers in those translation units. CMake must compile `util.c` with the main source for the symbol to resolve.

Risks: the declaration lacks parameter names and documentation beyond the file comment, so callers must refer to `util.c` for argument meaning. Any signature change must be synchronized with `main.c` and `util.c`.

Test signals: successful compilation/link of `test_random_directio` and runtime direct-I/O copy cycles confirm the header and implementation stay aligned.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_directio/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_session/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/random_session/main.c

Purpose: verifies that WiredTiger random number generation is sufficiently distinct across seeds and across sessions, especially when sessions are opened close together in time.

Important APIs, types, and functions: constants `N_SESSIONS` and `N_SEQUENTIAL_DIFFS` bound comparisons. `test_rng_seq` compares two seeded RNG streams. `test_rng_init` compares the first number from many different seeds. `main` opens WiredTiger, casts sessions to `WT_SESSION_IMPL`, and reads each session's `rnd_random` state with `__wt_random`.

Control flow: `main` parses standard test options, runs seed-sequence checks, creates `WT_TEST.random_session`, opens a small WiredTiger connection, then performs a single-session test by opening/closing one session at a time and checking adjacent first numbers differ in more than half the cases. It then opens ten sessions rapidly, runs 100 cycles, generates one number per session per cycle, and checks that each session's number differs from the first and from peers in more than half the comparisons. It closes sessions, closes the connection, removes the home unless preserved, and asserts `random_numbers_repeated` remains false.

State and persistence behavior: creates a temporary WiredTiger home but no tables. Important mutable state is per-session internal RNG state. The short sleeps reset timeslices to increase the chance sessions are opened close together, which is the collision scenario under test.

Dependencies and integration points: depends on internal `WT_SESSION_IMPL::rnd_random`, random initialization functions, public connection/session APIs, and `testutil_parse_opts`. It complements `random/main.c`, which checks the exact default sequence.

Risks: statistical assertions are simple thresholds, not formal randomness tests. Accessing `WT_SESSION_IMPL` ties the test to internal structure layout. The variable `random_numbers_repeated` is never set, so the final assertion is currently redundant.

Test signals: zero exit means seeded RNG streams and rapidly opened session RNGs differ often enough by full value and modulo 2048. Verbose mode prints the generated values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/random_session/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/rwlock/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/rwlock/main.c

Purpose: load and correctness test for WiredTiger's internal reader/writer lock implementation, referencing HELP-4355 rwlock collapse under load. It can also be compiled against POSIX rwlocks with `USE_POSIX` for comparison.

Important APIs, types, and functions: global `WT_RWLOCK rwlock`, optional `pthread_rwlock_t p_rwlock`, `running`, and `shared_counter` coordinate the test. `main` parses standard options with defaults of 100 threads and one million operations per thread, opens WiredTiger with `session_max=1000`, initializes locks, starts a dump thread, starts worker threads, times completion, and cleans up. `thread_rwlock` opens a session, takes a write lock every `READS_PER_WRITE` operations and read locks otherwise, updates/checks `shared_counter`, and releases the lock. `thread_dump` prints internal rwlock fields once per second in verbose mode.

Control flow: workers loop from 1 to `opts->nops`, choose read versus write lock based on modulus, acquire either WiredTiger or POSIX lock depending on compile-time macro, do a small atomic increment to prevent optimization, check correctness by reading/updating `shared_counter` and yielding while holding the lock, then unlock. `main` joins all workers, stops the dump thread, destroys the POSIX lock, and calls `testutil_cleanup`.

State and persistence behavior: creates a WiredTiger home from parsed options and opens a connection mostly to obtain valid `WT_SESSION_IMPL` objects for lock operations. The shared correctness state is in memory (`shared_counter`). No table data is persisted.

Dependencies and integration points: depends on internal locking APIs `__wt_rwlock_init`, `__wt_readlock`, `__wt_writelock`, `__wt_readunlock`, `__wt_writeunlock`, atomics, yield, epoch timing, pthreads, and testutil option parsing. Registered as `test_rwlock` with a generated `WT_HOME` argument.

Risks: high default concurrency can be expensive and scheduler-sensitive. `opts->running = false` is set by each worker but the dump thread uses the separate global `running`; this is harmless but confusing. Correctness assertions depend on `CHECK_CORRECTNESS` and intentionally hold locks across `__wt_yield`, increasing contention.

Test signals: successful completion prints elapsed seconds and exits zero. Verbose mode prints periodic internal lock state, useful for diagnosing reader/writer queue collapse or starvation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/rwlock/main.c -->
