# subset-b-009069 Research

Grouped research for the requested WiredTiger model, tooling, multiversion, and packing files. Each section title preserves the source path and is wrapped for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_basic/main.cpp -->
# sources/storage-engines/wiredtiger/test/model/test/model_basic/main.cpp

## Purpose
This is the foundational unit/integration test executable for the WiredTiger model layer. It validates `model::data_value`, basic key/value history behavior, row-store and column-store table verification against live WiredTiger, logged-table semantics, range truncation, oldest/stable timestamp rules, and debug-log replay verification.

## Important APIs, Types, and Functions
The file uses `model::kv_database`, `model::kv_table_ptr`, `model::kv_table_config`, `model::data_value`, `model::NONE`, and helpers from `model/test/wiredtiger_util.h`. The main scenarios are `test_data_value`, `test_model_basic`, `test_model_basic_wt`, `test_model_basic_column_wt`, `test_model_basic_logged`, `test_model_basic_logged_wt`, `test_model_truncate`, `test_model_truncate_wt`, `test_model_truncate_column_wt`, `test_model_oldest`, `test_model_oldest_wt`, and `test_model_debug_log_verify_wt`. WiredTiger-facing paths use `WT_CONNECTION`, `WT_SESSION`, `session->create`, and wrappers such as `wt_model_insert_both`, `wt_model_assert`, `wt_model_truncate_both`, `wt_model_set_oldest_timestamp_both`, and `verify_using_debug_log`.

## Control Flow
`main` parses shared test options, creates a temporary home directory, runs each scenario inside a `try` block, then removes the home unless `-p` was requested. Model-only tests directly mutate `kv_database` tables and assert expected snapshots. WiredTiger tests create a real table under a per-scenario subdirectory, perform paired model/WT operations, verify equality through `table->verify_noexcept(conn)`, deliberately perturb the model to prove verification can fail, and finally verify reconstruction through the debug log.

## State, Persistence, and Integration
The test uses a single `ENV_CONFIG` with table debug logging, retained logs, checkpoint retention, statistics, and small cache settings. State coverage includes timestamped update chains, non-timestamped globally visible updates, duplicate-key behavior with overwrite disabled, tombstones, column-store recnos, logged tables where timestamps are ignored, oldest timestamp monotonicity and restart behavior, and named debug-log verification for packed numeric keys. It integrates with the WiredTiger C API, common test utilities, model utility helpers, and debug-log parser support.

## Risks and Test Signals
This file is sensitive to semantic drift between the model and WiredTiger around timestamp visibility, logged table handling, range truncation boundaries, and persisted oldest timestamps. The strongest signals are direct return-code assertions, `wt_model_assert` comparisons at multiple read timestamps, `verify_noexcept` success/failure checks, and debug-log replay verification after close/reopen. Failures usually point to mismatched model history semantics or an instrumentation/debug-log regression rather than test harness noise.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_basic/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_checkpoint/main.cpp -->
# sources/storage-engines/wiredtiger/test/model/test/model_checkpoint/main.cpp

## Purpose
This executable validates the model's checkpoint semantics against WiredTiger. It covers stable-timestamp checkpoint visibility, named and unnamed checkpoints, prepared transaction checkpoint rules, restart-time checkpoint discovery, and logged table differences where stable timestamps do not filter logged updates the same way.

## Important APIs, Types, and Functions
The central types are `model::kv_database`, `model::kv_table_ptr`, `model::kv_checkpoint_ptr`, and `model::kv_transaction_ptr`. Model-only coverage is in `test_checkpoint` and `test_checkpoint_logged`; WiredTiger comparison paths are `test_checkpoint_wt`, `test_checkpoint_restart_wt`, and `test_checkpoint_logged_wt`. The test uses model checkpoint calls (`create_checkpoint`, `checkpoint`, `set_stable_timestamp`, `restart`) and WT helpers (`wt_model_ckpt_create_both`, `wt_model_ckpt_assert`, `wt_model_txn_begin_both`, `wt_model_txn_prepare_both`, `wt_model_txn_commit_both`, `wt_print_debug_log`).

## Control Flow
Each scenario builds a sequence of transactional inserts, advances stable timestamps, creates checkpoints, and asserts checkpoint reads for selected keys. The WT scenarios open multiple sessions to model concurrent transactions, create tables with `log=(enabled=false)` or `log=(enabled=true)`, then verify current table state and checkpoint state. Some scenarios close and reopen the database specifically so the debug log can be printed and replayed into a fresh `kv_database`.

## State, Persistence, and Integration
The file tests checkpoint state as a durable snapshot boundary: committed data before the stable timestamp should be visible, uncommitted or too-new data should be absent, and prepared transactions depend on prepare/commit/durable timestamps. `test_checkpoint_restart_wt` chains named checkpoints across multiple reopen cycles and prepared transactions to ensure retained debug-log metadata can reconstruct checkpoints after restart. Logged table scenarios intentionally ignore stable timestamps for logged data and validate that behavior in both model and WT paths.

## Risks and Test Signals
Checkpoint semantics are highly coupled to timestamp rules, prepared transaction durability, debug logging, and checkpoint retention. Risk areas include moving the stable timestamp backwards, committing prepared transactions with durable timestamps after stable, leaving prepared work in checkpoints, and interpreting logged table checkpoints. Test signals include `contains_any` checks for multiple values at one key, `verify_noexcept` against named checkpoints, debug-log and JSON replay parity, and model exceptions for illegal timestamp ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_checkpoint/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_rts/main.cpp -->
# sources/storage-engines/wiredtiger/test/model/test/model_rts/main.cpp

## Purpose
This executable validates rollback-to-stable, restart, and crash behavior in the model and in WiredTiger. It checks how stable timestamps bound durable state, how active/prepared transactions are handled by restarts and crashes, and how logged tables differ from non-logged timestamped tables.

## Important APIs, Types, and Functions
The file uses `model::kv_database`, `model::kv_table_ptr`, `model::kv_transaction_ptr`, `model::data_value`, subprocess helpers from `model/test/subprocess.h`, and WT/model bridge helpers from `wiredtiger_util.h`. Scenario functions include `test_rts`, `test_rts_wt`, `test_rts_crash_wt`, `test_restart_wt1`, `test_restart_wt2`, `test_restart_wt3`, `test_crash_wt1`, `test_crash_wt2`, `test_crash_wt3`, and `test_logged_wt`.

## Control Flow
`main` initializes a temporary home and runs all RTS scenarios. Model-only portions directly set stable timestamps, call `rollback_to_stable`, `restart`, or `crash`, and assert visible values. WT portions often execute setup in `in_subprocess` or `in_subprocess_abort` blocks to simulate clean shutdown or crash, then reopen the database in the parent and compare with model state using `wt_model_assert`. After each WT scenario, the debug log is replayed as an additional check.

## State, Persistence, and Integration
The scenarios distinguish rollback before any stable timestamp, rollback after setting stable, restart with and without explicit checkpoints, crash with no checkpoint, crash after checkpoint, and crash with active/prepared transactions. They also test that updates at timestamps lower than newly recovered stable state can still be applied after RTS/restart. Logged table coverage confirms that committed logged updates are not removed by RTS based on stable timestamp, while uncommitted transactions are still lost.

## Risks and Test Signals
Risk centers on crash/restart boundary conditions, especially when checkpoints, stable timestamps, active transactions, and prepared transactions overlap. The subprocess abort paths are important because normal process teardown would not exercise recovery. Strong test signals include stable timestamp equality after reopen, absence or presence of keys around stable boundaries, successful lower-timestamp writes after recovery, and debug-log verification after each scenario. Failures can indicate recovery semantic drift or model/WT mismatch in rollback visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_rts/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_transaction/main.cpp -->
# sources/storage-engines/wiredtiger/test/model/test/model_transaction/main.cpp

## Purpose
This executable validates transaction semantics in the WiredTiger model and compares them with real WiredTiger behavior. It covers snapshot isolation, write conflicts, read timestamps, commit timestamp changes within a transaction, prepared transactions, logged table timestamp behavior, column-store transaction behavior, rollback, reset snapshot, and truncation interactions with visibility and conflicts.

## Important APIs, Types, and Functions
Primary APIs include `model::kv_database::begin_transaction`, `model::kv_transaction::commit`, `rollback`, `prepare`, `set_commit_timestamp`, `reset_snapshot`, and table methods `insert`, `remove`, `truncate`, `get`, and `get_ext`. WT comparison uses helpers such as `wt_model_txn_begin_both`, `wt_model_txn_insert_both`, `wt_model_txn_prepare_both`, `wt_model_txn_commit_both`, `wt_model_txn_rollback_both`, `wt_model_txn_reset_snapshot_both`, and `wt_model_truncate_both`. Scenarios include basic, column-store, prepared, logged, visible-truncate, and conflict-truncate variants.

## Control Flow
The model-only scenarios build concurrent transactions and directly inspect table state and return codes. WT scenarios recreate the same sequences with two or more `WT_SESSION`s, then call model/WT paired helpers and final `verify_noexcept`. `main` runs all scenarios after parsing `test_util` options and cleans the test home unless preservation is requested.

## State, Persistence, and Integration
The file models transaction-private writes, committed history, read timestamp visibility, conflict detection against concurrent and snapshot-invisible writes, prepared state and prepare conflicts, logged tables where timestamps are ignored and prepare is unsupported, and column-store recnos. Truncation tests verify two edge behaviors: truncate skips records invisible to its transaction, and truncate fails with `WT_ROLLBACK` when it encounters uncommitted conflicting updates. WT integration uses row-store and column-store table formats and debug-log verification for the broad transaction paths.

## Risks and Test Signals
The highest-risk areas are timestamp assignment order within a transaction, prepared transaction read conflicts, and places where the test intentionally omits WT operations that would hang or abort. Logged table semantics are deliberately different from non-logged tables, so regressions may look like timestamp mismatches unless the table config is considered. Test signals include exact return-code parity, `WT_ROLLBACK`, `WT_PREPARE_CONFLICT`, exception assertions for illegal model operations, final table verification, and debug-log replay for the main transaction scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_transaction/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_workload/main.cpp -->
# sources/storage-engines/wiredtiger/test/model/test/model_workload/main.cpp

## Purpose
This executable tests the workload abstraction used by the WiredTiger model test framework. It verifies that scripted workloads can be constructed, run in the model, run in WiredTiger, parsed from text, generated randomly, and replayed through debug-log verification.

## Important APIs, Types, and Functions
The file depends on `model::kv_workload`, `model::kv_workload_generator`, `model::operation::*`, `model::kv_database`, and verification helpers `verify_workload` and `verify_using_debug_log`. Scenario functions are `test_workload_basic`, `test_workload_txn`, `test_workload_prepared`, `test_workload_restart`, `test_workload_crash`, `test_workload_generator`, and `test_workload_parse`.

## Control Flow
Each workload scenario builds a `kv_workload` using chained `operator<<` calls with operations such as `create_table`, `begin_transaction`, `insert`, `remove`, `truncate`, `prepare_transaction`, `commit_transaction`, `checkpoint`, `checkpoint_crash`, `crash`, `restart`, `set_stable_timestamp`, and `rollback_to_stable`. The workload is first executed in an in-memory `kv_database`, expected final values are asserted, then `verify_workload` runs the same workload against WiredTiger in a scenario-specific home directory. Parser tests stringify operations, parse them back, and compare operation equality.

## State, Persistence, and Integration
The tests cover non-timestamped updates, timestamped transactions, prepared transaction durable timestamps, rollback-to-stable, restart and crash persistence, checkpoint crash markers, and generated workloads. The generator test retries known issue workloads up to a bound and disables disaggregated storage in its spec because verification currently needs special handling. Parser coverage includes quoted strings, escapes, whitespace, hex integers, optional arguments, unsigned numeric keys/values, and operation equality.

## Risks and Test Signals
The workload layer is a central integration point between generated model operations and the WT runner. Risks include parser/stringifier drift, generated invalid workloads, mismatched operation return-code semantics, and missing debug-log representation for workload operations. Signals are final model value assertions, `verify_workload` model-vs-WT verification, debug-log replay after each concrete workload, bounded retries for known generator issues, and parser round-trip equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/model_workload/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/test_model.sh -->
# sources/storage-engines/wiredtiger/test/model/test/test_model.sh

## Purpose
This shell script is the simple test-suite driver for the model unit/integration executables built in the same directory. It runs the basic, checkpoint, RTS, transaction, and workload model tests in sequence.

## Important APIs, Types, and Functions
The script uses Bash, `set -e` for fail-fast execution, `BASH_SOURCE[0]` to find its own directory, and `set -x` to echo commands before execution. It directly invokes `test_model_basic`, `test_model_checkpoint`, `test_model_rts`, `test_model_transaction`, and `test_model_workload`.

## Control Flow
The script resolves `SCRIPT_PATH` to the directory containing the script, enables xtrace, and executes each test binary through an absolute path rooted at that directory. Because `set -e` is enabled, the first non-zero test exit aborts the script and propagates failure to the caller.

## State, Persistence, and Integration
The script does not manage test homes or cleanup itself; each executable handles its own temporary directory and preservation options. Its integration role is orchestration for build/test systems or local developers who need one command to execute all model tests.

## Risks and Test Signals
The main risks are missing executable build artifacts, incorrect invocation from non-build directories, or failure to include newly added model test binaries. Its test signal is binary-level exit status with xtrace output identifying the last command. It has no retry, filtering, or parallelism, so failures are straightforward but coarse.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/test/test_model.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/tools/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/model/tools/CMakeLists.txt

## Purpose
This CMake file declares the standalone model tools built from `test/model/tools`: the randomized/replay workload runner and the debug-log verifier.

## Important APIs, Types, and Functions
It includes `${CMAKE_SOURCE_DIR}/cmake/helpers.cmake` and uses the project helper `create_test_executable`. Two targets are declared: `model_test` from `model_test/main.cpp`, and `model_verify_debug_log` from `model_verify_debug_log/main.cpp`. Both link `wiredtiger_model` and `wiredtiger_model_test_common`, request C++ compilation with `CXX`, and opt out of `test_util` injection with `NO_TEST_UTIL`.

## Control Flow
CMake evaluation is declarative: include helper functions, then create the two test executables. There are no `add_test` registrations in this file, so these tools may be invoked by scripts, Evergreen tasks, or developers rather than as direct CTest cases from this file.

## State, Persistence, and Integration
The file is an integration bridge between the model library and executable tools. Linking both tools with model and model test common libraries gives them access to workload generation, WiredTiger runner helpers, debug-log parsing, and common verification utilities.

## Risks and Test Signals
Risks are build-level: missing helper definitions, library name changes, or accidentally linking test utility wrappers that conflict with these standalone tools. Successful configuration and compilation are the primary signals. Runtime behavior is covered by the tool sources themselves and by external invocations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/tools/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/tools/model_test/main.cpp -->
# sources/storage-engines/wiredtiger/test/model/tools/model_test/main.cpp

## Purpose
This is the standalone randomized/replay workload runner for the WiredTiger model. It can generate workloads, load workload files, run them in both the model and WiredTiger, compare per-operation return codes, verify final database contents in a child process, print workloads, preserve failures, and reduce counterexamples.

## Important APIs, Types, and Functions
Core functions are `run_and_verify`, `update_spec`, `load_spec`, `load_workload`, `reduce_counterexample_by_aspect`, `reduce_counterexample`, and `main`. Important types include `model::kv_workload`, `model::kv_workload_generator_spec`, `model::kv_workload_generator`, `model::kv_workload_runner_wt`, `model::kv_database`, `model::shared_memory`, `model::shared_memory`, `reduce_counterexample_context_t`, and the C `shared_verify_state` shared with the verifier subprocess.

## Control Flow
`main` parses CLI options for connection/table/generator config, seed, runtime/iteration bounds, workload length/table counts, print-only mode, preservation, and counterexample reduction. If workload files are supplied, it parses and runs each file. Otherwise it repeatedly generates workloads from a seeded generator until runtime and iteration criteria are met. `run_and_verify` runs the workload in the model, restarts the model to match recovery, writes `model_test.workload`, runs WT, compares return vectors, forks a verifier process, and checks the child exit status. On failure, `reduce_counterexample` tries to shrink the workload by sequences, tables, and operations.

## State, Persistence, and Integration
The tool creates and removes a WiredTiger home, optionally with a `kv_home` subdirectory for disaggregated storage. It writes the main workload file and may write `reduced.workload` in the failure home. It can merge connection and table configuration from command-line strings, config files, generated logging settings, and optional random timing stress settings. Verification opens the resulting WT database and compares every listed table with the model's expected state; disaggregated mode picks up the latest checkpoint first.

## Risks and Test Signals
This is a high-leverage testing tool, so determinism and diagnostics matter. Risks include mismatched model/WT return vector lengths, generated malformed workloads, failure reduction producing invalid schedules, unbounded core dumps during reduction, and config strings changing generator behavior unexpectedly. Strong signals are printed iteration/seed lines, exact operation index for return-code mismatch, child-process verification errors, saved reproducer workloads, and reduced counterexamples that still reproduce the failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/tools/model_test/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/tools/model_verify_debug_log/main.cpp -->
# sources/storage-engines/wiredtiger/test/model/tools/model_verify_debug_log/main.cpp

## Purpose
This standalone tool verifies a WiredTiger database by reconstructing model state from the table debug log or from a JSON debug-log dump, then comparing that reconstructed state with the database and optionally a named checkpoint.

## Important APIs, Types, and Functions
The key function is `verify_timestamps`, which compares WT `query_timestamp` results for oldest and stable timestamps with the reconstructed `model::kv_database`. `main` parses `-C`, `-c`, `-h`, `-j`, and `-?`, opens the database read-only, lists tables with `model::wt_list_tables`, loads state with `model::debug_log_parser::from_debug_log` or `from_json`, resolves an optional checkpoint, and calls `db.table(t)->verify(conn, ckpt)` for each table.

## Control Flow
The tool builds a connection config starting from `readonly=true,log=(enabled=false)` and appends any `-C` overrides. It opens WT, loads tables and debug-log model state inside exception-handled blocks, validates global timestamps, then verifies each table. Errors print a specific diagnostic and exit failure; `-?` prints usage and exits success.

## State, Persistence, and Integration
The tool does not mutate the database. It depends on WT table debug logging having captured enough information for reconstruction. With `-j`, it can verify a JSON log produced by other tooling instead of reading the log from the open database. Checkpoint verification routes through the model checkpoint object so historical snapshot state can be compared with a named WT checkpoint.

## Risks and Test Signals
Risks include opening with incompatible read-only config, missing or incomplete debug-log metadata, table-name mismatches, timestamp formatting/parsing drift, and checkpoint names absent from the reconstructed model. Test signals are explicit table verification messages, oldest/stable timestamp mismatch errors, parser load failures, and `verify` exceptions for table or checkpoint divergence.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/tools/model_verify_debug_log/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/multiversion/wt_multiversion.sh -->
# sources/storage-engines/wiredtiger/test/multiversion/wt_multiversion.sh

## Purpose
This Bash script exercises WiredTiger workgen multiversion compatibility between the current checkout and an older stable WiredTiger release. It builds the last-stable tree on demand, copies the current multiversion runner into it, and runs release-specific compatibility checks.

## Important APIs, Types, and Functions
The script defines `last_stable=4.2`, `last_stable_dir=wiredtiger_4.2/`, and `last_stable_branch=mongodb-4.2`. `setup_last_stable` clones `https://github.com/wiredtiger/wiredtiger.git`, checks out the stable branch, runs `bash reconf`, configures with Python and diagnostic support, and builds with `make -j 10`. `run_check` echoes and executes a command, exiting on failure.

## Control Flow
If the stable tree does not exist, the script clones and builds it. It then sets paths for the current and stable `bench/workgen/runner/multiversion.py`, copies the current runner into the stable tree, and runs four checks: current runner for release 4.4, current runner with `--keep`, stable-tree runner with `--keep --release 4.2`, and current runner again with `--keep --release 4.4`. Success prints `Success.` and exits 0.

## State, Persistence, and Integration
The script creates a sibling `wiredtiger_4.2` directory and leaves it for reuse. It mutates that clone by copying the latest multiversion runner over the stable runner path. It depends on network access, Git, autotools/reconf prerequisites, Python support, diagnostic build support, and the relative location of `bench/workgen/runner/multiversion.py`.

## Risks and Test Signals
Risks include network or branch availability failures, build dependency drift, stale stable clone contents, relative path changes, and incompatibilities hidden by copying the current runner into the stable tree. The test signal is command exit status through `run_check`; the echoed commands identify which multiversion pass failed.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/multiversion/wt_multiversion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/packing/CMakeLists.txt

## Purpose
This CMake file declares the WiredTiger packing test executables and registers them with CTest. It covers generic packing, variable-length integer packing, and 4-bit integer-array packing.

## Important APIs, Types, and Functions
The file uses `create_test_executable` to build `test_packing` from `packing-test.c` with executable name `packing-test`, `test_intpack` from `intpack-test3.c` with executable name `intpack-test3`, and `test_int4bpack` from `int4bpack-test.c` with executable name `int4bpack-test`. It registers CTest names `test_packing`, `test_intpack`, and `test_int4bpack`, and labels `test_packing` as `check`.

## Control Flow
CMake creates the three executables, then adds three tests that run the resulting targets. There is no conditional logic, custom config, or direct registration for `intpack-test.c` and `intpack-test2.c`; those files remain auxiliary/manual or historical unless included elsewhere.

## State, Persistence, and Integration
The build file integrates packing tests into the broader WT build system through helper macros. Runtime tests do not need persistent database homes because they exercise internal packing APIs in process.

## Risks and Test Signals
Build risks include source renames, helper macro changes, and tests not being registered or labeled consistently. A notable coverage risk is that only `intpack-test3.c` and `int4bpack-test.c` are registered here, so changes affecting the older `intpack-test.c` and `intpack-test2.c` may not be exercised by this CTest file. CTest pass/fail status is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/int4bpack-test.c -->
# sources/storage-engines/wiredtiger/test/packing/int4bpack-test.c

## Purpose
This C test validates WiredTiger's 4-bit/nibble-oriented positive integer array packing implementation and signed zigzag helpers. It combines human-readable encoding dumps, boundary checks, buffer-size error checks, partial decoding, and randomized fuzzing.

## Important APIs, Types, and Functions
The file includes `test_util.h` and exercises internal APIs `__wt_4b_pack_array`, `__wt_4b_unpack_array`, `__wt_4b_size_array`, `__4b_unpack_init`, `__4b_unpack_posint_ctx`, `__wt_encode_signed_as_positive`, and `__wt_decode_positive_as_signed`. Scenario functions include `test_positive_integers`, `test_signed_integers`, `test_pairs_of_integers`, `test_small_int_arrays`, `test_bigger_int_arrays`, `test_extreme_values`, `test_alignment_boundaries`, `test_exact_fit_and_enomem`, `test_truncated_and_overcount_decode`, `test_partial_decode_resume`, and `test_random_fuzz`.

## Control Flow
`main` initializes the WT library, runs deterministic coverage first, then fuzzes positive and signed arrays. Round-trip helpers encode values into fixed buffers, assert encoded length equals `__wt_4b_size_array`, decode through pointer-advancing APIs, verify full consumption, print encoded bytes/bits, and compare decoded values. Error tests intentionally use too-small buffers or truncated inputs and assert `ENOMEM` or `EINVAL`.

## State, Persistence, and Integration
The test is in-memory only. Its state is local buffers, pointer cursors, deterministic arrays, and a seeded `WT_RAND_STATE`. It integrates directly with internal packing code and test utility allocation/assertion/random helpers. Printed output documents the byte and bit representation for manual inspection, but correctness relies on assertions.

## Risks and Test Signals
Risk areas include nibble alignment flips across element boundaries, boundary values near encoding length changes, UINT64 and INT64 extremes, exact-fit buffer handling, truncated decode validation, and resumable context decoding. The fuzz loops broaden coverage across random lengths and values. Strong signals are pointer consumption checks, expected packed-size checks, explicit error-code assertions, and deterministic edge-case arrays.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/int4bpack-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/intpack-test.c -->
# sources/storage-engines/wiredtiger/test/packing/intpack-test.c

## Purpose
This is a stress/performance-style round-trip test for WiredTiger variable-length unsigned integer packing. It repeatedly packs and unpacks powers of two and verifies that values survive encoding.

## Important APIs, Types, and Functions
The file includes `test_util.h`, initializes the WT library with `__wt_library_init`, and uses `__wt_vpack_uint`, `__wt_vunpack_uint`, `WT_INTPACK64_MAXSIZE`, `testutil_check`, and `testutil_assert`. The only test body is `main`.

## Control Flow
`main` initializes a buffer, then loops ten million outer iterations. For each iteration, it walks shift values from 0 to 45 in steps of 5, computes `1ULL << s`, packs it, records encoded length, asserts that length is within the max size, unpacks it, and asserts equality. It counts calls and prints the total.

## State, Persistence, and Integration
The test is entirely in-memory and has no persistent state. It uses an oversized buffer initialized to `0xff` to avoid compiler uninitialized warnings and to provide room beyond the maximum pack size. A disabled `#else` block contains a `memmove` baseline useful for local performance comparison but not active in normal test builds.

## Risks and Test Signals
Risk coverage is narrow but high-volume: it detects regressions in unsigned varint round-trip correctness for several magnitude classes. It does not test signed packing, malformed inputs, or full boundary coverage. Signals are assertion failures, `__wt_*` return codes, encoded length limits, and the printed number of calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/intpack-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/intpack-test2.c -->
# sources/storage-engines/wiredtiger/test/packing/intpack-test2.c

## Purpose
This small diagnostic test prints the byte encodings for positive and negative powers of two using WiredTiger variable-length integer packing. It is useful for inspecting encoding shape across magnitude boundaries.

## Important APIs, Types, and Functions
The file uses `__wt_library_init`, `__wt_vpack_uint`, `__wt_vpack_int`, `WT_INTPACK64_MAXSIZE`, and test utility assertions. The only function is `main`.

## Control Flow
`main` initializes a fixed buffer, then iterates `i` from 1 up to but not including `1LL << 60`, doubling each time. For each value, it packs the unsigned value, asserts the encoded length is within the maximum, prints the decimal value and hex bytes, then packs and prints the corresponding negative signed value.

## State, Persistence, and Integration
The test is in-memory and produces stdout as its main diagnostic artifact. It does not unpack and verify values, so it complements rather than replaces round-trip tests. It depends on internal packing APIs and the common test utility initialization path.

## Risks and Test Signals
The file is mainly observational. It can expose unexpected encoding length or byte changes for powers of two, but because it does not decode the result its automated correctness signal is limited to pack return codes and max-size assertions. It is not registered by the local packing CMake file, so routine CTest coverage may not include it unless another build path does.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/intpack-test2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/intpack-test3.c -->
# sources/storage-engines/wiredtiger/test/packing/intpack-test3.c

## Purpose
This C test validates round-trip signed and unsigned WiredTiger variable-length integer packing over dense ranges around important boundaries. It extends coverage beyond simple powers of two by checking values near zero, INT16_MAX, INT32_MAX, INT64_MAX, and successively halved large ranges.

## Important APIs, Types, and Functions
The file declares `test_value` and `test_spread`. `test_value` exercises `__wt_vpack_int`, `__wt_vunpack_int`, `__wt_vpack_uint`, and `__wt_vunpack_uint`, with size checks against `WT_INTPACK64_MAXSIZE`. `test_spread` loops over a contiguous range and calls `test_value`.

## Control Flow
`main` computes a `range` of 1025 and a safe start near `INT64_MAX`, then calls `test_spread` for a large range around zero and for ranges around signed 16-bit, signed 32-bit, and signed 64-bit maxima. It then repeatedly halves the large start value and tests a spread around each point. `test_value` packs/unpacks a signed value and an unsigned cast of the same bit pattern, verifies equality, and verifies the unpack pointer consumed exactly the bytes written.

## State, Persistence, and Integration
The test is in-memory only. Each value gets a fresh buffer initialized to `0xff`, local pointer cursors, and local signed/unsigned variables. It depends on internal integer packing APIs and test utility initialization; `__wt_library_init` is called in `test_value`, so the library is initialized repeatedly during the run.

## Risks and Test Signals
This file targets off-by-one and boundary-class regressions in variable-length integer encodings. Pointer-consumption assertions catch decoders that return the right value but consume the wrong length. A likely defect in the unsigned mismatch check compares `sinput` and `soutput` again instead of checking `uinput` and `uoutput`, reducing automated unsigned verification strength. The file is the registered `test_intpack` source in the packing CMake file, so failures are visible through CTest.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/packing/intpack-test3.c -->
