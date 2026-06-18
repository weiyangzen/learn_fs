# subset-b-009067 research

Grouped research for the WiredTiger fuzz, huge, live_restore, manydbs, and model test sources in subset B. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/fuzz_util.c -->
# sources/storage-engines/wiredtiger/test/fuzz/fuzz_util.c

Purpose: shared libFuzzer support for WiredTiger fuzz targets. It owns the process-global `FUZZ_GLOBAL_STATE fuzz_state`, lazily opens a small WiredTiger home, and provides helpers for splitting byte input into multiple logical arguments.

Important APIs and functions: `fuzzutil_setup` creates a per-process home named `WT_TEST_<pid>`, recreates it, calls `wiredtiger_open` with create/cache/statistics settings, and opens one session. `fuzzutil_sliced_input_init` searches the input for a caller-provided separator using `memmem`, stores pointers and lengths into heap arrays, and succeeds only when exactly `req_slices` are present. `fuzzutil_sliced_input_free` releases those arrays. `fuzzutil_slice_to_cstring` copies a byte slice into a NUL-terminated string.

Control flow and state: the first fuzz invocation initializes `fuzz_state`; later invocations reuse the same connection/session. Sliced input is zero-copy with respect to the fuzzer buffer; only the slice pointer/length arrays are allocated. On parse failure the helper frees partial arrays and returns `false`.

Dependencies and integration: depends on `fuzz_util.h`, `test_util.h`, WiredTiger public API, and GNU `memmem`. It is built as the shared `fuzz_util` library and consumed by fuzz targets such as config and modify fuzzers.

Risks and test signals: no teardown exists for `fuzz_state`, which is acceptable for fuzzer process lifetime but leaks by design. Invalid separator counts reject many early corpus inputs. `fuzzutil_sliced_input_init` assumes nonzero separator size and does not pre-count separators, so malformed input still allocates briefly. Test signal is libFuzzer exercising targets without worker home collisions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/fuzz_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/fuzz_util.h -->
# sources/storage-engines/wiredtiger/test/fuzz/fuzz_util.h

Purpose: public interface for WiredTiger fuzz target helpers. It centralizes the global connection/session state and the sliced-input abstraction used when one fuzz byte string needs to represent multiple logical inputs.

Important APIs and types: `FUZZ_GLOBAL_STATE` stores `WT_CONNECTION *conn` and `WT_SESSION *session`; `extern FUZZ_GLOBAL_STATE fuzz_state` exposes the process-global instance. `fuzzutil_setup` initializes the connection/session lazily. `FUZZ_SLICED_INPUT` stores `const uint8_t **slices`, `size_t *sizes`, and `num_slices`. `fuzzutil_sliced_input_init/free` manage those arrays, and `fuzzutil_slice_to_cstring` converts a slice into an allocated C string.

Control flow and state: the header exposes ownership conventions but not cleanup for the global WiredTiger handles. Callers own strings returned by `fuzzutil_slice_to_cstring` and must call `fuzzutil_sliced_input_free` after successful sliced input initialization.

Dependencies and integration: includes `test_util.h`, which supplies WiredTiger types, test assertions/checking helpers, and standard support used by implementation files. It is included by `fuzz_util.c`, `modify/fuzz_modify.c`, and other fuzz targets.

Risks and test signals: because the API returns raw pointers and heap memory, callers must free per-invocation strings and sliced arrays. The `/* ![fuzzutil sliced input api] */` markers suggest documentation extraction or code snippet tests may rely on this block remaining stable. Coverage is through fuzz target build and execution under the fuzz CMake configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/fuzz_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/modify/fuzz_modify.c -->
# sources/storage-engines/wiredtiger/test/fuzz/modify/fuzz_modify.c

Purpose: libFuzzer target for WiredTiger modify packing and application code. It turns arbitrary bytes into a base value plus one `WT_MODIFY`, packs it through internal helpers, grows a buffer, and applies the modify.

Important APIs and functions: `LLVMFuzzerTestOneInput` is the fuzzer entry point. It calls `fuzzutil_setup`, casts the session to `WT_SESSION_IMPL`, opens a `metadata:` cursor to satisfy internal helper requirements, calls `__wt_modify_pack`, `__wt_modify_max_memsize_unpacked`, `__wt_buf_set_and_grow`, and `__wt_modify_apply_item`.

Control flow and state: inputs smaller than 10 bytes return immediately. `data[0] % size` selects the initial value length; the remainder becomes modify data; `data[buf.size] % size` selects the modify offset. The cursor, scratch item, and buffer are freed before returning. The WiredTiger connection/session are reused via fuzz global state.

Dependencies and integration: includes `fuzz_util.h` and relies on WiredTiger internal symbols/macros from the test build. CMake links this target with `fuzz_util`, WiredTiger, test utilities, and libFuzzer.

Risks and test signals: this target deliberately drives internal modify paths with arbitrary offsets and sizes. It assumes `buf.size < size`, which holds because `data[0] % size` is used. The fuzzer checks for crashes, assertions, sanitizer failures, and invalid memory handling in modify pack/apply behavior rather than asserting semantic output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fuzz/modify/fuzz_modify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/huge/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/huge/CMakeLists.txt

Purpose: build and register the `test_huge` executable. This test stresses oversized keys and values in WiredTiger objects.

Important APIs and behavior: `create_test_executable(test_huge SOURCES huge.c)` builds the binary from `huge.c`. `define_test_variants` registers the `small|-s` variant and labels it `check`, which means normal check smoke runs execute the small bounded mode rather than the full multi-gigabyte sweep.

Control flow and state: the CMake file has no runtime state. It delegates variant expansion to the repository's test CMake helpers.

Dependencies and integration: relies on top-level WiredTiger test CMake macros and the `huge.c` source. The `small` variant maps directly to `huge.c` option `-s`.

Risks and test signals: the full executable can allocate up to 4 GiB and open WiredTiger with a 10 GiB cache, so check integration intentionally constrains CI exposure. A useful test signal is that the small variant remains under check labels while full runs are left for explicit stress execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/huge/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/huge/huge.c -->
# sources/storage-engines/wiredtiger/test/huge/huge.c

Purpose: standalone C test for very large WiredTiger keys and values across file/table row-store and column-store configurations. It inserts, verifies, and removes a single large item for multiple sizes.

Important APIs and functions: `CONFIG` describes URI/config/column-store key style. `lengths` spans 20 bytes, 1 MiB, 250 MiB, 1 GiB, 2 GiB, 3 GiB, and roughly 4 GiB minus 1 MiB. `run` creates the object, sets either a large key or value, commits an explicit transaction, searches back, compares with `memcmp`, removes the record, and closes the connection. `main` parses `-h` and `-s`, allocates `big`, initializes it with `a`, loops configurations and sizes, then removes the work directory.

Control flow and state: row-store configurations test both large keys and large values; column-store configurations only test large values because recno keys are scalar. Explicit transactions and cursor reset are used to avoid pinning a page that itself exceeds eviction thresholds.

Dependencies and integration: uses `test_util.h`, WiredTiger public cursor/session/connection APIs, and test allocation/removal helpers. The CMake small variant limits allocation to `SMALL_MAX` (1 MiB), despite the usage text saying "up to 1GB".

Risks and test signals: full mode is memory and disk heavy. The critical signal is exact byte equality after readback and successful removal/close. The test is sensitive to platform `size_t`, allocation limits, cache configuration, and eviction behavior for huge single updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/huge/huge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/huge/smoke.sh -->
# sources/storage-engines/wiredtiger/test/huge/smoke.sh

Purpose: smoke wrapper for the huge-item test.

Important behavior: the script enables `set -e` and runs `$TEST_WRAPPER ./t -s`. The `-s` flag maps to the small runtime path in `huge.c`, and `$TEST_WRAPPER` lets the surrounding test harness inject environment, timeout, sanitizer, or platform wrappers.

Control flow and state: there is no persistent state in the script. The underlying test creates and removes its own WiredTiger test home.

Dependencies and integration: expects to run in the directory where `./t` is the huge test executable or wrapper target. It is intended for `make check` style smoke execution, complementing the CMake `small|-s` variant.

Risks and test signals: any nonzero exit fails the smoke due to `set -e`. The script only exercises bounded huge-item coverage, so regressions specific to multi-gigabyte sizes require explicit full test runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/huge/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/live_restore/helper.sh -->
# sources/storage-engines/wiredtiger/test/live_restore/helper.sh

Purpose: shared shell helper for live restore test scripts.

Important API: `live_restore_binary_path` points to `./test/cppsuite/test_live_restore`. `run_test` executes that binary with one argument string, captures the exit status, and accepts success or exit code 137. Other nonzero codes print diagnostic command/exit information and exit with the same code.

Control flow and state: the helper does not parse arguments itself and does not modify persistent files. It assumes callers source it from the build directory and pass a complete option string as `$1`.

Dependencies and integration: sourced by `short_test.sh` and `long_test.sh`. It depends on bash function syntax and the C++ suite `test_live_restore` binary being built at the expected relative path.

Risks and test signals: exit 137 is accepted because live restore tests may intentionally kill themselves. This can mask accidental SIGKILL/OOM failures if they also surface as 137, so surrounding logs are important. The unquoted `$live_restore_binary_path $1` intentionally allows option-string splitting but would not handle paths or values containing spaces.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/live_restore/helper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/live_restore/long_test.sh -->
# sources/storage-engines/wiredtiger/test/live_restore/long_test.sh

Purpose: longer scripted live restore regression suite run from the build directory.

Important behavior: it sources `../test/live_restore/helper.sh` and invokes `run_test` with several `test_live_restore` configurations: 10 iterations with 20k operations and 20 collections, the same with per-directory database mode `-D`, background-thread debug mode `-b -t 1`, crash/death runs with 50k operations and 12 threads, recovery runs with `-r`, and matching per-directory crash/recovery coverage.

Control flow and state: tests run sequentially and stop on helper failure. Death-mode invocations may terminate with exit 137, which helper accepts. Recovery runs rely on state left by preceding death-mode runs.

Dependencies and integration: depends on `helper.sh`, `test/cppsuite/test_live_restore`, and the build-directory relative path layout. It exercises live restore threading, CRUD replay, collection fanout, per-directory database layout, and recovery.

Risks and test signals: the script is intentionally expensive and order-dependent. A failure in a death run can cascade into recovery. Accepted 137 status needs log review to distinguish intended self-kill from resource exhaustion. Strong signals are successful recovery after death-mode runs and completion under both standard and `-D` layouts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/live_restore/long_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/live_restore/short_test.sh -->
# sources/storage-engines/wiredtiger/test/live_restore/short_test.sh

Purpose: short live restore smoke suite for build-directory execution.

Important behavior: the script sources `../test/live_restore/helper.sh`, runs a 10-iteration single-collection workload with 1000 operations and INFO-level logging, then runs a small death/recovery pair: `-i 2 -l 2 -d -o 10` followed by `-i 1 -l 2 -r -o 10`.

Control flow and state: commands execute sequentially through `run_test`. The recovery invocation depends on files produced by the preceding death-mode invocation.

Dependencies and integration: same helper and `test_live_restore` binary as long test, but with reduced operation count and collection count for faster validation.

Risks and test signals: useful smoke coverage for live restore startup, CRUD, intentional death, and recovery, but it does not cover high collection counts, per-directory DB mode, or high thread counts from the long suite. Exit 137 is accepted by helper for intentional kills.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/live_restore/short_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/live_restore/take_backup.py -->
# sources/storage-engines/wiredtiger/test/live_restore/take_backup.py

Purpose: utility script for creating a physical backup of a wtperf-generated database to use as the source directory in live restore performance tests.

Important APIs and functions: `main` assumes home `WT_TEST_0_0` and backup directory `WT_TEST_0_0_backup`. It removes any previous backup directory, creates a new one, opens WiredTiger through the Python binding, opens a `backup:` cursor, iterates backup file names, and copies each from home to backup with `shutil.copyfile`.

Control flow and state: the script is intended to run from `build/bench/wtperf` after the `btree-500m-populate` workload has produced `WT_TEST_0_0`. It mutates the local filesystem by deleting/recreating the backup directory. WiredTiger session, cursor, and connection are closed explicitly.

Dependencies and integration: appends `../../lang/python` to `sys.path`, imports `wiredtiger_open`, and uses standard `os`, `shutil`, and `sys`. It integrates with live restore perf tests outside the core CMake test flow.

Risks and test signals: the hard-coded home and destructive backup directory removal make the working directory contract important. It copies only files listed by the backup cursor, which is correct for WiredTiger backup but assumes paths are simple children of the home. Successful completion creates a full backup directory with no explicit verification beyond copy errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/live_restore/take_backup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/manydbs/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/manydbs/CMakeLists.txt

Purpose: build and register the `test_manydbs` executable.

Important behavior: `create_test_executable(test_manydbs SOURCES manydbs.c)` builds the binary. On Windows, CTest launches it through `powershell.exe $<TARGET_FILE:test_manydbs>` because the test has issues under the normal CTest process. Other platforms register `add_test(NAME test_manydbs COMMAND test_manydbs)`. The test is labeled `check`.

Control flow and state: CMake only declares build/test metadata and platform-specific launch behavior.

Dependencies and integration: relies on project test macros, the `WT_WIN` platform variable, and `manydbs.c`. It places the many-database condition-variable reset test in normal smoke coverage.

Risks and test signals: the platform wrapper hints at resource/process isolation sensitivity on Windows. A useful signal is cross-platform registration preserving the `check` label while still isolating Windows execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/manydbs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/manydbs/manydbs.c -->
# sources/storage-engines/wiredtiger/test/manydbs/manydbs.c

Purpose: stress test for multiple simultaneous WiredTiger connections and condition-variable wake/reset behavior under idle and light write workloads.

Important APIs and functions: `get_stat` opens a `statistics:` cursor and reads selected connection stats. `run_ops` writes random-sized byte values to random databases. `main` parses `-D maxdbs`, `-h dir`, and `-I` idle mode; creates per-database homes; opens up to `dbs` connections rotating transaction sync configs; optionally creates `table:main`; records `WT_STAT_CONN_COND_AUTO_WAIT_RESET`; sleeps and optionally writes over 30 seconds; then checks reset thresholds.

Control flow and state: arrays track connections, sessions, cursors, and baseline reset counts. Each database lives under `WT_TEST/WT_TEST.<i>`. In idle mode cursors are not allocated and no table is created. Non-idle mode writes to a quarter of databases per cycle.

Dependencies and integration: uses `test_util.h`, WiredTiger public APIs, internal random helpers, and stat IDs. CMake registers it as `test_manydbs`.

Risks and test signals: thresholds are platform-specific for spurious condition-variable wakeups, with looser allowances on NetBSD, Windows, and macOS. The test intentionally has wall-clock sleeps and can be timing-sensitive. Strong signals are no idle resets beyond threshold and resets under light workload staying below a fraction of waits.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/manydbs/manydbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/model/CMakeLists.txt

Purpose: defines the shared `wiredtiger_model` C++17 library and pulls in model tests and tools.

Important behavior: `add_library(wiredtiger_model SHARED ...)` compiles core model files, driver parsers/generators/runners, and verification code. `target_include_directories` exposes `src/include` publicly and adds build config, WiredTiger source includes, and test third-party includes privately. Compile options require `-std=c++17` and `-Wnon-virtual-dtor`. The library links `Iconv::Iconv`, dynamic loading libraries, and `wt::wiredtiger`. It then adds `test` and `tools` subdirectories.

Control flow and state: build metadata only; no runtime state. The duplicate `target_include_directories` block is redundant but harmless.

Dependencies and integration: integrates with nlohmann JSON in third-party includes, WiredTiger internal/public headers, iconv for UTF-8 decoding, dlopen support for library path discovery, and the WiredTiger target.

Risks and test signals: shared-library linkage and private internal headers mean ABI/build layout changes can break model tooling. Iconv availability is required. The model tests/tools provide validation that all listed sources compile and link as a coherent testing library.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/core.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/core.cpp

Purpose: compile-time bridge between model constants and WiredTiger internal constants.

Important behavior: includes `model/core.h` and `wt_internal.h`, then uses `static_assert(k_txn_max == WT_TXN_MAX)` inside namespace `model`. `core.h` can assert public or locally replicated constants, but `WT_TXN_MAX` requires internal headers, so this `.cpp` performs the final check.

Control flow and state: no runtime control flow or persistent state. The file exists to fail compilation if the model's transaction maximum diverges from WiredTiger internals.

Dependencies and integration: depends on internal WiredTiger headers being available to the model library target. It integrates with the `wiredtiger_model` build as a guard against semantic drift.

Risks and test signals: if WiredTiger changes transaction ID limits, the model library stops compiling until `core.h` is updated. This is a desirable early signal because MVCC visibility and snapshot behavior depend on matching ID bounds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/core.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/data_value.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/data_value.cpp

Purpose: implementation of the model's generic key/value representation and WiredTiger cursor conversion helpers.

Important APIs and functions: defines constants `NONE` and `ZERO`. `data_value::unpack` decodes a raw buffer with a single WiredTiger format character into `int64_t`, `uint64_t`, `std::string`, or `byte_vector` using `__wt_struct_unpack`. `wt_type` maps variant alternatives back to WT format strings. Stream operators print byte vectors as hex and values in human-readable form. `get_wt_cursor_key/value` and `set_wt_cursor_key/value` bridge `WT_CURSOR` varargs APIs using cursor key/value formats.

Control flow and state: all conversion paths reject null buffers, null/empty formats, multi-field structs, unsupported `x`, and type mismatches. Length prefixes are skipped before checking the single format character. `WT_ITEM` values are copied to/from `byte_vector` and temporary `WT_ITEM`.

Dependencies and integration: depends on `model/data_value.h`, `model/util.h::parse_uint64`, WiredTiger public API, and internal `__wt_struct_unpack`.

Risks and test signals: the model currently does not support compound formats or type `x`; workload generation is similarly narrow. Cursor setters require exact variant/type compatibility and reject `NONE`. Verification and log replay heavily depend on these conversions matching WiredTiger packing behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/data_value.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_database.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/kv_database.cpp

Purpose: implements the in-memory model database that owns tables, active transactions, checkpoints, and oldest/stable timestamps.

Important APIs and functions: `kv_database_config::from_string` parses `disaggregated` and `leader`. `create_table` enforces unique names and creates `kv_table`. `create_checkpoint` captures transaction snapshot, oldest timestamp, and stable timestamp, with nameless checkpoint overwrite semantics. `begin_transaction` allocates increasing model txn IDs and snapshots active transactions. `txn_snapshot_nolock` excludes active in-progress transactions and, for checkpoints, prepared transactions. `restart`, `start_nolock`, and `rollback_to_stable_nolock` simulate WiredTiger recovery and rollback-to-stable.

Control flow and state: recursive mutexes protect tables and transactions; separate mutexes protect checkpoints and timestamps. `clear_nolock` resets timestamps, rolls back active transactions, and clears tables. Clean restart first rolls back active transactions and creates a checkpoint; crash restart does not.

Dependencies and integration: uses `kv_table`, `kv_transaction`, `kv_checkpoint`, snapshots, `config_map`, and WiredTiger checkpoint naming constants. It is driven by workload runners and debug-log parser.

Risks and test signals: lock ordering is documented and important. Snapshot rules approximate WiredTiger behavior; prepared checkpoint handling and disaggregated precise-checkpoint simulation are high-risk areas. Test signals come from matching model return codes/state against WiredTiger and from verification after restart/RTS.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_database.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_table.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/kv_table.cpp

Purpose: implements table-level operations for the in-memory key/value model, including timestamp-aware reads, writes, truncation, rollback-to-stable, and verification cursor creation.

Important APIs and functions: `type_by_key_value_format` detects column-store tables from `key_format == "r"`. `get/get_ext` read directly, through checkpoints, or through transactions. `insert`, `update`, `remove`, and `truncate` create `kv_update` objects and attach them to `kv_table_item`s and transactions. Non-transactional variants run through `with_transaction` and `kv_transaction_guard`. `fix_timestamps` and `rollback_updates` delegate to items by key.

Control flow and state: `_data` is a sorted `std::map<data_value, kv_table_item>` protected by `_lock`, but items are never removed to keep returned references stable. Logged/non-timestamped tables normalize timestamps to `k_timestamp_none`. Truncate scans ranges and also checks neighboring prepared updates for known issue `WT-13232`.

Dependencies and integration: depends on `kv_database`, `kv_transaction`, `kv_table_item`, `kv_update`, and verification classes. Workload runners call this for model execution.

Risks and test signals: never removing map elements preserves references but can retain deleted key shells. Truncate prepared-conflict behavior is explicitly tied to a known WiredTiger issue. Signals are model/WiredTiger return-code equivalence and table verifier agreement.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_table.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_table_item.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/kv_table_item.cpp

Purpose: implements per-key update chains with MVCC visibility, transaction conflict checks, prepare conflicts, timestamp fixing, and rollback.

Important APIs and functions: `add_update_nolock` validates non-timestamped/timestamped mixing, detects transaction conflicts against snapshots and uncommitted updates, enforces insert/update existence constraints, and inserts updates sorted by commit timestamp. `get` implements read-own-writes, non-transactional reads, transactional snapshot visibility, prepare conflicts, and stable/durable timestamp filtering. `contains_any` checks all visible updates at a timestamp. `fix_timestamps` removes placeholder timestamp updates, sets final commit/durable timestamps, and reinserts. `rollback_to_stable` removes prepared, out-of-snapshot, or too-new durable updates.

Control flow and state: `_updates` is a sorted deque of shared `kv_update` pointers guarded by `_lock`. Failed conflicts mark the owning transaction failed and throw `WT_ROLLBACK`. Rollback paths remove transaction references to break ownership cycles.

Dependencies and integration: used by `kv_table`; depends on `kv_update`, `kv_transaction`, checkpoints, and WiredTiger error constants.

Risks and test signals: visibility rules are the model's most sensitive behavior. Prepared reads use prepare timestamp ordering, while other operations mostly use commit timestamp ordering. Incorrect reinsertion or durable timestamp filtering would cause verifier mismatches after prepare/commit/RTS/checkpoint workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_table_item.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_transaction.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/kv_transaction.cpp

Purpose: implements model transaction lifecycle, timestamp validation, prepare/commit/rollback state transitions, and update bookkeeping.

Important APIs and functions: `add_update` stamps WiredTiger metadata onto updates and records table/key/update triples. `commit` validates failed state, prepared durable timestamp requirements, durable >= commit, stable timestamp constraints, fixes placeholder update timestamps through tables, marks committed, removes transaction back-pointers from updates, and unregisters the transaction from the database. `prepare` validates state, disallows non-timestamped/logged table updates, checks stable timestamp ordering, and marks prepared. `rollback` marks rolled back, removes all updates from tables, and unregisters. `set_commit_timestamp` validates and stores timestamps for later updates.

Control flow and state: transaction state is atomic; `_lock` protects timestamp fields and update lists. `_nontimestamped_updates` tracks updates created before a final commit timestamp was known. `_wt_id` and `_wt_base_write_gen` are preserved for debug-log imported transactions.

Dependencies and integration: owned by `kv_database`, referenced by `kv_update`, and driven by model runner/debug log parser.

Risks and test signals: destructor-safe guards can only print commit exceptions, so unexpected guard failures may be easy to miss. Prepared durable timestamp and stable timestamp rules are high-value test signals for matching WiredTiger abort/error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_transaction.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_transaction_snapshot.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/kv_transaction_snapshot.cpp

Purpose: implements transaction snapshot visibility predicates for model-generated snapshots and snapshots imported from WiredTiger metadata.

Important APIs and functions: `kv_transaction_snapshot_by_exclusion::contains` excludes updates whose transaction ID is newer than `_exclude_after` or appears in `_exclude_ids`. `kv_transaction_snapshot_wt::contains` first compares WiredTiger base write generation, then applies snapshot min/max and excluded ID set to WiredTiger transaction IDs.

Control flow and state: snapshots are immutable after construction. The WT-style snapshot treats older write generations as visible, newer generations as invisible, and only compares transaction IDs within the same write-generation era.

Dependencies and integration: used by `kv_database::txn_snapshot_nolock`, checkpoint creation, debug-log checkpoint metadata replay, and `kv_table_item` visibility filtering. Depends on `kv_update` methods exposing model and WT transaction metadata.

Risks and test signals: write-generation handling is critical after restart/log replay because transaction IDs alone are not globally meaningful. Incorrect max-exclusive behavior or exclusion set handling would surface as verification mismatches after checkpoints, recovery, or imported log snapshots.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/kv_transaction_snapshot.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/random.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/random.cpp

Purpose: thin C++ wrapper around WiredTiger's internal pseudo-random generator for deterministic model workload generation.

Important APIs and functions: constructor seeds `WT_RAND_STATE` with `__wt_random_init_seed`. `next_double` and `next_float` scale `__wt_random` output to `[0, 1]` using `uint32_t` max. `next_index` returns a modulo index for a collection length. `next_uint64` combines two 32-bit random values into one 64-bit value.

Control flow and state: all state is the embedded `WT_RAND_STATE`; methods advance it in place. The header also supplies range helpers, probability macros, and weight initialization macros used by the workload generator.

Dependencies and integration: includes `model/random.h`, which imports `wt_internal.h`. Used heavily by `kv_workload_generator` for reproducible table, key, operation, timestamp, and stress-configuration choices.

Risks and test signals: `next_index(0)` would divide by zero; callers must ensure nonempty collections. Modulo and floating scaling are sufficient for tests but not uniform for all ranges. Deterministic seeds are the key test signal for reproducing generated workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/random.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/util.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/util.cpp

Purpose: shared utilities for configuration parsing, RAII-adjacent support, shared memory, UTF-8 byte recovery, path discovery, disaggregated storage helpers, eviction, extension lookup, and table listing.

Important APIs and functions: `config_map::from_string/parse_array/merge` parse WiredTiger-like config strings into nested maps/arrays. `shared_memory` wraps POSIX `shm_open`, `ftruncate`, `mmap`, immediate unlink, and `munmap`. `decode_utf8` uses iconv to convert JSON Unicode escapes back to byte values from `wt printlog -u`. Path helpers find directory/executable/model library/build directory. `wt_disagg_config_string` builds palite precise-checkpoint config. `wt_disagg_pick_up_latest_checkpoint` queries page-log checkpoint metadata and reconfigures WiredTiger. `wt_evict` opens a debug eviction cursor. `wt_list_tables` scans metadata.

Control flow and state: config parsing is hand-written and preserves nested values as variants. Shared memory is process-shared and zero-initialized. Disagg checkpoint pickup opens sessions/page logs and uses guards for cleanup.

Dependencies and integration: uses POSIX APIs, iconv, dladdr/dirname/readlink, WiredTiger public/internal APIs, and model data conversion helpers. Used by debug-log parser and WT workload runner.

Risks and test signals: parser is narrower than full WiredTiger config grammar. `executable_path` checks `readlink` incorrectly for zero rather than negative and does not NUL-terminate, although typical use may tolerate this. Disagg helpers are platform/build-layout sensitive. Failures surface in model tools, log replay, and disaggregated workload execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/verify.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/core/verify.cpp

Purpose: compares a WiredTiger table against the in-memory model table, optionally at a checkpoint.

Important APIs and functions: `kv_table_verify_cursor::has_next` skips deleted model items. `verify_next` advances the model cursor and compares the expected key/value, allowing any value visible at the same timestamp/checkpoint via `contains_any`. `get_prev` supports diagnostic messages. `kv_table_verifier::verify` opens a WiredTiger session and table cursor, optionally with `checkpoint=<name>`, iterates all WT records, compares to the model, checks for extra model records, and finally calls `session->verify(..., "strict")`, ignoring `EBUSY` with a warning.

Control flow and state: verification cursor is explicitly not thread-safe and holds an iterator into the model table map. RAII guards close session/cursor. Verbose diagnostic paths exist but `_verbose` is false by default.

Dependencies and integration: used by `kv_table::verify` and model tests/tools. Depends on data conversion helpers and WiredTiger cursor/session APIs.

Risks and test signals: key ordering must match `data_value` ordering and WiredTiger cursor order for supported formats. Strict verify may be skipped on `EBUSY`, leaving content comparison as primary signal. Mismatches throw `verify_exception` with the observed and previous model pair.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/core/verify.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/debug_log_parser.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/driver/debug_log_parser.cpp

Purpose: replays WiredTiger debug logs, either binary log scan or `wt printlog -u` JSON, into the model database so recovered WT state can be verified against modeled history.

Important APIs and functions: JSON `from_json` overloads decode log operation structs; binary `from_debug_log` overloads call WiredTiger internal unpackers for col/row put/remove/truncate, timestamps, prev LSN, and commit headers. `metadata_apply` interprets metadata row puts, maps file IDs to files/tables, creates model tables from colgroups/table/file metadata, tracks checkpoint metadata, and updates base write generation. `metadata_checkpoint_apply` creates WT-style checkpoint snapshots. `apply` overloads perform model operations for row/column changes and transaction timestamps. Static `from_debug_log` uses `__wt_log_scan`; static `from_json` parses a JSON array.

Control flow and state: parser state maps file IDs/files/tables, stores metadata configs, accumulates per-transaction checkpoint metadata, and tracks base write generation. Commit records begin a model transaction, replay operations, then finalize; system `prev_lsn` may trigger `database.start`.

Dependencies and integration: depends on nlohmann JSON, `wt_internal.h`, model database/table/transaction APIs, `decode_utf8`, and config parsing. Used by model verification tools.

Risks and test signals: unsupported log operations such as modify variants throw. Metadata support is intentionally narrow and rejects column groups with extra nesting. Correct signals are successful replay followed by `database.start()` and table verification matching actual WiredTiger files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/debug_log_parser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload.cpp

Purpose: implements parsing, validation, and execution dispatch for text-serializable key/value workloads.

Important APIs and functions: `operation::parse` parses `name(arg,...)` strings with quote/escape handling and constructs the matching operation variant. It supports transaction lifecycle, checkpoints/crashes/restart/RTS, table creation, get/insert/remove/truncate, timestamps, and WT/model config operations. `kv_workload::assert_timestamps` validates monotonic stable/oldest timestamps, operation timestamps relative to stable, and disaggregated stable-timestamp requirements. `kv_workload::verify` checks table existence, updates table visibility after disaggregated crash/checkpoint behavior, and tracks checkpoint timestamp restoration. `run` executes against the model runner; `run_in_wiredtiger` executes against the WT runner.

Control flow and state: workload is a deque of `kv_workload_operation` entries, each carrying an operation variant and optional sequence number. Verification simulates metadata state enough to catch invalid references before execution.

Dependencies and integration: includes `kv_workload.h`, model and WT workload runners, `parse_uint64`, and WiredTiger constants.

Risks and test signals: parser currently assumes unsigned numeric keys/values for text input. `get` values are not yet compared (`FIXME-WT-14863`). A valid workload should pass `verify`, run in both model and WT, and produce comparable return-code streams.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_generator.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_generator.cpp

Purpose: random workload generator that creates serial-equivalent transaction/special-operation sequences, derives dependencies, assigns valid timestamps, and emits a randomized interleaving for model/WT execution.

Important APIs and functions: default specs set probabilities for table counts, transaction operations, special operations, key reuse, logging, prepared transactions, and timing stress. `table_context::choose_existing_key` picks tracked live keys. `sequence_traversal` maintains runnable sequences under dependency and optional barrier constraints. `assign_timestamps` fills placeholders for prepare/commit/durable/stable/oldest timestamps. `create_table` emits row or column table creation. `generate_transaction` creates transaction sequences with reads, writes, removes, truncates, prepare/commit/rollback, and optional commit timestamp setting. `run` orchestrates generation, dependency creation, timestamp assignment, interleaving, and final validation.

Control flow and state: generator tracks tables, live key sets, transaction IDs, sequence DAG, database config, and random state. Special operations create barriers; overlapping key ranges create ordering dependencies; RTS blocks all earlier/later sequences. Disaggregated mode disables unsupported column/RTS/prepared paths and enforces stable timestamps before checkpoints/closes.

Dependencies and integration: uses `kv_workload_generator.h`, workload operations, random wrapper, and model utility helpers. Tools/tests call static `generate` and stress/log config helpers.

Risks and test signals: dependency logic is central; missed overlap can produce WT rollbacks not represented in the serial model. Narrow supported data formats limit coverage. Generated workloads self-check with `kv_workload::verify`, and seed replay is the main debugging signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_generator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_runner_wt.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_runner_wt.cpp

Purpose: executes model workloads against a real WiredTiger home, including intentional crash/restart handling and disaggregated storage support.

Important APIs and functions: `session_context` owns a WT session and lazily opens per-table cursors. `run` creates shared memory for return codes/state, applies initial config operations before opening, then forks a child to run/resume workload. Parent detects intentional crashes via shared state and resumes after crash operations. `do_operation` overloads map operation variants to WiredTiger APIs: transactions, checkpoints, crash kill, table create, cursor search/insert/remove/truncate, timestamps, rollback_to_stable, restart, and config storage. `wiredtiger_open_nolock` composes base/disagg/override config, opens WT, picks up latest disagg checkpoint, steps up leader role, and sets stable/oldest timestamps. `remove_local_files` clears WT files for disaggregated starts.

Control flow and state: shared state records configs, table URIs for recovery, return codes, crash index, and exceptions. Locks protect connection, sessions, and table URI maps. Crashes use `SIGKILL` in the child to avoid core files.

Dependencies and integration: depends on WT public/internal APIs, POSIX fork/wait/signal/dir APIs, `shared_memory`, data conversion cursor helpers, and disagg utilities.

Risks and test signals: Unix process semantics are required. Shared-state size caps table URI count/length. Child exceptions are marshaled back as strings. `get` still ignores read value. Strong signals are correct resume after intentional crash and matching return codes/verification versus the model.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_runner_wt.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_sequence.cpp -->
# sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_sequence.cpp

Purpose: implements sequence dependency helpers for generated workloads.

Important APIs and functions: `overlaps_with` checks whether this sequence's insert/remove/truncate operations touch keys or ranges touched by another sequence. `contains_key` checks exact key or range intersection for one table. `must_finish_before` adds a dependency edge from this sequence to another and a reverse unblocks edge.

Control flow and state: overlap detection iterates operation variants and only considers write-like operations that affect key ranges. Truncate range intersection checks endpoint containment and full containment. Dependencies are stored in vectors on the sequence objects.

Dependencies and integration: used by `kv_workload_generator` to preserve serial-equivalent semantics while later interleaving independent transactions. Depends on operation variants and `data_value` ordering.

Risks and test signals: the overlap model ignores read-only `get` and non-key special operations by design. Correctness depends on `data_value` comparisons matching table key ordering. Missed overlap dependencies can create unexpected WT conflicts; overly broad dependencies reduce concurrency coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/driver/kv_workload_sequence.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/core.h -->
# sources/storage-engines/wiredtiger/test/model/src/include/model/core.h

Purpose: foundational model constants, aliases, and exception types.

Important APIs and types: defines `timestamp_t`, `txn_id_t`, and `write_gen_t`; constants for none/latest/max timestamps, none/max transaction IDs, and write generation bounds; and exception classes `model_exception`, `wiredtiger_exception`, `wiredtiger_abort_exception`, and `known_issue_exception`. It mirrors public/internal WiredTiger values such as `WT_TS_MAX`, `WT_TS_NONE`, and `WT_TXN_NONE`, with static assertions where headers allow.

Control flow and state: header-only type and constant definitions, no mutable state. `wiredtiger_exception` captures a WiredTiger error code and formats messages through session or global WiredTiger strerror functions. `known_issue_exception` stores a ticket identifier.

Dependencies and integration: includes `wiredtiger.h` and standard exception/string/limits headers. `core.cpp` completes the `WT_TXN_MAX` assertion using internal headers. Every model core and driver file depends on these definitions.

Risks and test signals: constants must stay aligned with WiredTiger internals or MVCC/recovery modeling becomes invalid. Non-thread-safe `wiredtiger_exception` constructors that use global strerror are documented. Compile-time assertions are the main drift signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/data_value.h -->
# sources/storage-engines/wiredtiger/test/model/src/include/model/data_value.h

Purpose: declaration of the model's generic key/value type and cursor conversion API.

Important APIs and types: `byte_vector` represents arbitrary WT_ITEM bytes. `base_data_value` is a `std::variant<std::monostate, int64_t, uint64_t, std::string, byte_vector>`. `data_value` inherits the variant, provides `create_none`, `unpack` overloads for raw buffer, byte vector, string, and `WT_ITEM`, `none`, and `wt_type`. Constants `NONE` and `ZERO` are declared. Stream operators and cursor helpers `get_wt_cursor_key/value` and `set_wt_cursor_key/value` are declared.

Control flow and state: the header defines value semantics only; concrete conversion behavior lives in `data_value.cpp`. `NONE` is represented by `std::monostate` and is used throughout the model as deleted/not-found sentinel.

Dependencies and integration: includes `model/core.h`, `wiredtiger.h`, and standard variant/vector/string headers. Used by tables, updates, workload operations, verification, and WT runner cursor code.

Risks and test signals: inheriting from `std::variant` exposes variant operations directly, which is convenient but broad. Only single-field WT formats are currently supported by implementation. Correct equality/order behavior from the variant is central to `std::map<data_value, kv_table_item>` and verification ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/model/src/include/model/data_value.h -->
