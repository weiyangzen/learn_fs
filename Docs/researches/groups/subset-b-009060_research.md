# Research: subset-b-009060

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2695_checksum/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt2695_checksum/main.c

## Purpose
WT-2695 is a C-suite checksum smoke and stress test for WiredTiger's internal CRC32C implementations. It validates known CRC32C vectors, hardware and software parity, seeded cumulative CRC behavior, random payloads, and unaligned buffers.

## Important APIs, Types, and Functions
- Uses `test_util.h` harness types, especially `TEST_OPTS`, `WT_RAND_STATE`, `testutil_parse_opts`, `testutil_recreate_dir`, `testutil_cleanup`, `testutil_assertfmt`, and allocation helpers.
- Calls `wiredtiger_open` only to initialize a standard test home and statistics logging.
- Exercises internal checksum APIs: `__wt_checksum`, `__wt_checksum_sw`, `__wt_checksum_with_seed_sw`, and external selector `wiredtiger_crc32c_with_seed_func`.
- `check` centralizes equality assertions with byte length and diagnostic text.
- `cumulative_checksum` applies a seeded checksum function across fixed-size chunks and verifies equivalence with one-shot CRC.

## Control Flow
`main` parses options, recreates the home directory, opens WiredTiger, initializes random state, and allocates a 128 KiB data buffer plus a 32-byte `0xff` buffer. It then runs fixed vectors for zero bytes, all-`0xff` bytes, `"123456789"`, and `"The quick brown fox jumps over the lazy dog"`, including chunked cumulative calculations where length permits. It follows with 1000 power-of-two random buffers, 1000 random-length random buffers, and a 16x16 matrix of short lengths and misalignments.

## State and Persistence Behavior
The test creates a WiredTiger home with statistics logging but does not create tables or persistent user data. The relevant state is in memory: deterministic expected checksum constants, random payload bytes, and cumulative seed values. The unaligned checks deliberately pass shifted pointers into stack data.

## Dependencies and Integration Points
This test depends on WiredTiger internal checksum symbols and the CRC32C dispatch function. It integrates with the csuite runner through the standard `TEST_OPTS` home handling. s390x has guarded skips for seeded software CRC checks due to `FIXME-WT-12067`.

## Risks and Test Signals
Failures indicate CRC vector mismatch, hardware/software divergence, bad seeded CRC composition, or unaligned-read bugs. Random coverage is broad but not deterministic unless the underlying harness seed is fixed. The test is platform-sensitive on s390x because seeded software CRC assertions are disabled there.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2695_checksum/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2719_reconfig/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt2719_reconfig/main.c

## Purpose
WT-2719 fuzzes runtime `WT_CONNECTION::reconfigure` with many valid configuration fragments to catch parser, server restart, and configuration interaction bugs.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS`, `WT_RAND_STATE`, `WT_SESSION`, `WT_EVENT_HANDLER`, and standard test utility helpers.
- `list` contains reconfiguration fragments for cache, checkpoint, compatibility, eviction, file manager, logging, shared cache, statistics, statistics logging, and verbose categories.
- `handle_message` suppresses verbose event output.
- `on_alarm` aborts and prints the active config if a reconfiguration hangs.
- `reconfig` wraps `opts->conn->reconfigure`, installs a 60-second alarm, and hard-fails on nonzero return.

## Control Flow
The program opens a clean WiredTiger home, opens a session, initializes random state, and allocates a config buffer sized from the number of fragments. It first applies each fragment alone. It then builds random concatenations starting from each fragment, avoiding illegal combinations of `shared_cache` with `cache_size`, and reconfigures with those compound strings. Before cleanup, it disables `statistics_log.on_close` to prevent close-time failures if random options disabled statistics.

## State and Persistence Behavior
No user tables are created. The test mutates live connection-level state: server threads, cache sizing, logging/statistics options, file manager settings, and verbose output. The persistent home exists only as a configured WiredTiger environment.

## Dependencies and Integration Points
The test depends on runtime reconfiguration support for each listed option and on signal/alarm behavior. It is integrated as a csuite executable and uses the event handler interface to avoid noisy verbose messages.

## Risks and Test Signals
The main signal is any reconfigure error or timeout. Because random concatenations can hit unusual option ordering, it is useful for last-wins and server lifecycle regressions. Coverage deliberately avoids known invalid shared-cache/cache-size conflicts, so it does not validate error handling for those combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2719_reconfig/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2909_checkpoint_integrity/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt2909_checkpoint_integrity/main.c

## Purpose
WT-2909 tests checkpoint integrity under injected filesystem write failures. A child process populates two related tables through the `fail_fs` extension, failures are injected around checkpointing, and the parent reopens the home with the normal filesystem to verify recovery and data/index consistency.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS`, `WT_CURSOR`, `WT_SESSION`, `WT_EVENT_HANDLER`, `WT_RAND_STATE`, `fork`, `execv`, `waitpid`, `setenv`, `freopen`, and `setrlimit`.
- `check_results` opens recovered tables and indices, walks both main tables in lockstep, and verifies all secondary indexes.
- `generate_key`, `generate_value`, and `create_big_string` provide deterministic expected data from record number and stored random integer.
- `enable_failures` and `disable_failures` configure `WT_FAIL_FS_ENABLE`, `WT_FAIL_FS_WRITE_ALLOW`, and `WT_FAIL_FS_READ_ALLOW`.
- `run_check_subtest_range` binary-searches the number of allowed writes where recovery crosses from too-early failure to checkpoint-success behavior.
- `subtest_main` loads `WT_FAIL_FS_LIB` with `early_load` and `environment=true`; `subtest_populate` performs transactional writes and targeted checkpoint failure injection.

## Control Flow
The top-level `main` parses options, defaults to 50,000 records, and either dispatches a `subtest`/`subtest_close` child mode or runs parent orchestration. Parent mode calibrates the failure threshold unless `-o` supplies a fixed allowed-write count, then runs both early-exit and close-after-failure child variants. Each child creates `table:subtest`, `table:subtest2`, and three indexes, writes matching records in transactions, takes an initial checkpoint after the first insert, enables failure injection near 1% of the workload, and attempts a checkpoint. The parent removes/recreates homes between subtests and always verifies recovered content afterward.

## State and Persistence Behavior
Persistent state includes two tables, one indexed table, secondary indexes, log files, stdout/stderr files in the home, and possibly a partially written checkpoint. Transactions keep the two tables synchronized. Recovery must leave a prefix of records where both tables and all indexes agree. `subtest_close` intentionally tests cleanup/close after an expected filesystem failure; normal subtest exits immediately after expected failure.

## Dependencies and Integration Points
The test depends on Unix process APIs and does not run on Windows. It requires the `fail_fs` extension shared library and build-directory discovery via `-b`/`testutil_build_dir`. It integrates with csuite row/column variants through `-t r` and `-t c`.

## Risks and Test Signals
Hard failures include unrecoverable homes, missing tables, table count mismatch, index count mismatch, wrong values, unexpected child failures, or inability to calibrate the threshold after retries. Calibration is approximate and nondeterministic, so the harness treats missing both success/failure sides as `EAGAIN` and retries. One call in fixed-`-o` mode passes `opts->nrecords` as the `close_test` boolean, effectively always true for nonzero records; that is a noteworthy maintenance risk.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2909_checkpoint_integrity/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2909_checkpoint_integrity/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/wt2909_checkpoint_integrity/smoke.sh

## Purpose
This smoke wrapper runs the WT-2909 checkpoint integrity executable in both row-store and column-store modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Parses optional `-b <builddir>` and forwards it as `-b` to the test binary for extension discovery.
- Uses `TEST_WRAPPER` if set by the harness.

## Control Flow
The script resolves the test binary either from its first non-option argument or from `$binary_dir/test_wt2909_checkpoint_integrity`, where `binary_dir` defaults to the script directory. It invokes the binary twice: once with `-t r` and once with `-t c`.

## State and Persistence Behavior
The script itself creates no state. The invoked test creates and removes WiredTiger homes and may create child stdout/stderr files.

## Dependencies and Integration Points
It is copied into the build tree by CMake csuite definitions and assumes `TEST_WRAPPER` may prefix execution. The `-b` option is essential when the fail filesystem extension is not discoverable relative to the copied script.

## Risks and Test Signals
Any failing row or column run exits the script due to `set -e`. Manual execution outside the build directory must pass the binary path or set `binary_dir`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt2909_checkpoint_integrity/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3120_filesys/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt3120_filesys/main.c

## Purpose
WT-3120 validates that a simple filesystem extension can be loaded early, used for a small table workload, closed, and followed by a normal reopen with data intact.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS`, `WT_SESSION`, `WT_CURSOR`, `wiredtiger_open`, and standard test utility helpers.
- Loads `WT_FAIL_FS_LIB` through `extensions=(...=(early_load=true))`.
- Uses string-key/string-value table operations through the URI in `opts->uri`.

## Control Flow
The test parses options, recreates the home, builds an extension path from the build directory, and opens WiredTiger with fail filesystem extension early-loaded. It creates a string table, inserts keys `a` and `b`, closes the cursor/session/connection to force data to disk, reopens without the extension, and verifies the two records in order.

## State and Persistence Behavior
The table is persisted across close and reopen. Statistics logging is enabled in both open configurations. No failure injection is enabled; the extension load itself is the focus.

## Dependencies and Integration Points
The test depends on the fail filesystem shared library, `testutil_build_dir`, and extension loading. It integrates with the csuite binary options for home, URI, and build directory.

## Risks and Test Signals
Failure signals include extension load failure, close/reopen failure, missing records, wrong key/value ordering, or unexpected extra records. It is a narrow smoke test: it does not exercise fail_fs failure controls.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3120_filesys/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3184_dup_index_collator/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt3184_dup_index_collator/main.c

## Purpose
WT-3184 checks that duplicating an index cursor with a custom collator preserves enough key/value state to avoid truncated-key compare failures and returns the expected indexed value.

## Important APIs, Types, and Functions
- Defines `WT_COLLATOR index_coll` using `index_compare`.
- Uses `wiredtiger_struct_unpack(session, ..., "uu", ...)` to unpack index and primary key parts from packed index keys.
- `item_to_int`, `compare_int_items`, and `print_int_item` interpret `WT_ITEM` payloads as 32-bit integers while avoiding misaligned loads.
- Uses `session->open_cursor(session, NULL, cursor, NULL, &cursor1)` to duplicate the positioned cursor.

## Control Flow
The test opens a clean home, registers `index_coll`, creates `table:main` with unpacked item key/value formats, and creates `index:main:index` on column `v` with the custom collator. It inserts one record with key `13` and value `17`, searches the index by value, duplicates the index cursor, and asserts both original and duplicate return value `17`.

## State and Persistence Behavior
The table and secondary index are persistent within the test home, though no reopen is performed. Cursor state after `search` is the critical state under test; duplication must preserve the positioned index cursor.

## Dependencies and Integration Points
The test depends on custom collator registration and WiredTiger's packed struct format for index keys. It integrates with the C API cursor duplication path and index cursor value retrieval.

## Risks and Test Signals
Failures point to collator comparison receiving malformed/truncated packed keys, cursor duplication losing state, or index cursor value mismatch. The test only inserts one record, so it is surgical rather than broad coverage of duplicate-key ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3184_dup_index_collator/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3338_partial_update/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt3338_partial_update/main.c

## Purpose
WT-3338 stress-tests partial update construction and application. It compares WiredTiger's modify application and `wiredtiger_calc_modify` output with the independent `testutil_modify_apply` helper.

## Important APIs, Types, and Functions
- Uses global `WT_MODIFY entries[MAX_MODIFY_ENTRIES]`, random state, and replacement byte buffer.
- `modify_build` creates random modify vectors, including zero-length data and zero-size replacements.
- `compare` reports the first mismatch and dumps original/local/library buffers.
- `modify_run` constructs a fake `WT_CURSOR`, calls `__wt_modify_apply_api`, `testutil_modify_apply`, and `wiredtiger_calc_modify`.
- Uses internal buffer APIs `__wt_buf_set` and `__wt_buf_free` through `WT_SESSION_IMPL`.

## Control Flow
After opening a WiredTiger connection/session, `modify_run` initializes replacement data and loops 10,000 outer runs. Each outer run starts from a random short initial value and performs 1000 inner mutation rounds. For each round, it lowercases the current value, copies it, applies random modify vectors via WiredTiger and testutil implementations, compares results, asks WiredTiger to calculate a modify vector from the old to new value, applies that vector, and compares again. `WT_NOTFOUND` from `wiredtiger_calc_modify` is treated as no useful modify vector and skipped.

## State and Persistence Behavior
The test does not create application tables; it uses a real session only to support internal buffer and modify logic. The mutable state is the in-memory WT_ITEM buffers and fake cursor value.

## Dependencies and Integration Points
This is tightly coupled to WiredTiger internals (`WT_SESSION_IMPL`, `__wt_modify_apply_api`) and test utility modify semantics. It validates both the public `wiredtiger_calc_modify` API and lower-level apply path.

## Risks and Test Signals
Any divergence between local and library modify results aborts with detailed buffers. Random vectors exercise overlapping, empty, insertion, deletion, and replacement cases, but exact coverage depends on RNG. Because it creates no persistent table, it does not validate reconciliation or recovery of modifies.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3338_partial_update/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3363_checkpoint_op_races/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt3363_checkpoint_op_races/main.c

## Purpose
WT-3363 detects operations that block unexpectedly behind a slow checkpoint. It runs repeated delayed checkpoints alongside worker threads issuing create/drop/bulk/cursor operations and aborts if any worker stops making progress for too long.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS`, `TEST_PER_THREAD_OPTS`, `pthread_create/join`, `WT_EVENT_HANDLER`, `WT_RAND_STATE`, and shared operation helpers such as `op_bulk`, `op_create`, `op_cursor`, `op_drop`, `op_bulk_unique`, and `op_create_unique`.
- Connection config enables `timing_stress_for_test=[checkpoint_slow]`.
- `do_checkpoints` runs forced checkpoints and tolerates `EBUSY`/`ENOENT`.
- `do_ops` randomly chooses one of six operations.
- `monitor` samples per-thread operation counters and aborts if a counter is unchanged over half the checkpoint delay.

## Control Flow
The test exits immediately unless `TESTUTIL_ENABLE_TIMING_TESTS` is set because runtime is 15 minutes. When enabled, it opens a 1 GiB-cache database with timing stress, starts one checkpoint thread, ten operation threads, and one monitor thread. All threads run until `RUNTIME` elapses. Main joins operation, monitor, and checkpoint threads, prints success, and cleans up.

## State and Persistence Behavior
The workload creates and drops objects and may optionally populate data depending on test options. Persistence is incidental; the key state is per-thread progress counters plus database metadata/object handles under checkpoint contention.

## Dependencies and Integration Points
The file depends on test operation helpers defined elsewhere in the same csuite test target and on timing-stress support. It integrates with smoke wrapper variants with and without `-d`.

## Risks and Test Signals
The primary signal is an abort from `monitor`, preserving a core for blocked-operation diagnosis. Long runtime and timing dependence make it sensitive to slow machines. The counter array initialization uses `memset(last_ops, 0, sizeof(int) + N_THREADS)`, which appears smaller than the array and is a maintenance risk, though stack values are overwritten as counters advance.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3363_checkpoint_op_races/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3363_checkpoint_op_races/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/wt3363_checkpoint_op_races/smoke.sh

## Purpose
This smoke wrapper invokes the WT-3363 checkpoint-operation race executable in default and data-enabled modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Uses `$TEST_WRAPPER` to allow the harness to prefix execution.

## Control Flow
The script runs `./test_wt3363_checkpoint_op_races` and then `./test_wt3363_checkpoint_op_races -d`.

## State and Persistence Behavior
The script creates no state directly. The binary creates WiredTiger test homes and, unless timing tests are enabled, may exit immediately.

## Dependencies and Integration Points
It assumes execution from the directory containing the test binary. It is wired into make/ctest smoke flow.

## Risks and Test Signals
Because the binary is timing-gated, a smoke run can pass without running the 15-minute workload unless the environment flag is set. Any binary failure stops the script.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3363_checkpoint_op_races/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3874_pad_byte_collator/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt3874_pad_byte_collator/main.c

## Purpose
WT-3874 verifies that removal with a custom collator respects logical key equality when padding bytes differ.

## Important APIs, Types, and Functions
- Defines `WT_COLLATOR my_coll` where `my_compare` compares only the first byte of each `WT_ITEM`.
- Uses a `key_format=u,value_format=u` table with `collator=my_coll`.
- Uses log-enabled WiredTiger open to put the scenario through normal logged table behavior.

## Control Flow
The test opens a clean home, registers the collator, creates `table:main`, inserts a 20-byte key whose first byte is `a` and remaining bytes are `X`, checkpoints, then changes the same buffer so the first byte remains `a` and padding becomes `Y`. It removes using the new logical key and closes.

## State and Persistence Behavior
The key and value share the same `WT_ITEM` buffer. A checkpoint persists the inserted version before removal. The removal must locate the stored key via collator semantics rather than raw byte equality.

## Dependencies and Integration Points
The test exercises C API collator registration, row-store key comparison, checkpointing, and cursor remove. It depends on the collator being consulted when matching keys fetched from storage.

## Risks and Test Signals
An assertion or remove failure indicates WiredTiger compared raw padded bytes where the collator should define equality. The test covers one simple key and does not reopen after removal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt3874_pad_byte_collator/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4105_large_doc_small_upd/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt4105_large_doc_small_upd/main.c

## Purpose
WT-4105 stresses small `WT_CURSOR::modify` updates against large documents while a snapshot transaction pins cache content, looking for modify hangs or cache pressure regressions.

## Important APIs, Types, and Functions
- Uses `WT_MODIFY`, `WT_ITEM`, two sessions, signal `alarm`, and a custom `WT_EVENT_HANDLER`.
- Table config uses huge key/value limits, small leaf pages, and 1 MiB memory pages.
- `on_alarm` aborts if a modify call exceeds the timeout.
- `handle_error` can suppress a small number of expected cursor API messages, though the main path does not set `ignore_errors`.

## Control Flow
The test opens a 1 GiB cache database, creates `table:large`, inserts two 1 MiB values, then begins a long-running snapshot transaction in the first session to pin cache. A second session repeatedly modifies both documents 1023 times, replacing 26 bytes at a moving offset. For non-sanitizer builds, each modify is guarded by a 15-second alarm. Offsets advance like an append sequence and wrap at document size.

## State and Persistence Behavior
The table contains two large values and many in-place logical modifies. One open snapshot transaction intentionally pins older cache state. Updates are committed in separate snapshot transactions in the second session. No explicit final verification is performed; success is absence of timeout/error.

## Dependencies and Integration Points
This test depends on modify support for row and column-store variants supplied by the smoke script. It integrates with sanitizer flags to disable alarms on slow instrumentation builds.

## Risks and Test Signals
The main signal is timeout or modify/transaction failure. Because verification is temporal rather than content-based, it catches performance/hang regressions more than data correctness. The connection config redundantly includes `statistics_log` twice, harmless but noisy.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4105_large_doc_small_upd/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4105_large_doc_small_upd/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/wt4105_large_doc_small_upd/smoke.sh

## Purpose
This smoke wrapper runs WT-4105 in row-store and column-store modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Resolves test binary from an optional argument or `$binary_dir/test_wt4105_large_doc_small_upd`.
- Uses `$TEST_WRAPPER` for harness integration.

## Control Flow
After binary resolution, it invokes the binary with `-t r` and `-t c`.

## State and Persistence Behavior
No direct script state; the binary creates its WiredTiger home and large table.

## Dependencies and Integration Points
Assumes CMake copies the script next to the binary or that the binary path is passed manually.

## Risks and Test Signals
Either row or column mode failure exits the script. Manual execution outside the build tree needs an explicit binary path or `binary_dir`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4105_large_doc_small_upd/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4117_checksum/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt4117_checksum/main.c

## Purpose
WT-4117 smoke-tests the public WiredTiger CRC32C function selector API against fixed known vectors.

## Important APIs, Types, and Functions
- Calls `wiredtiger_crc32c_func()` to obtain `uint32_t (*)(const void *, size_t)`.
- `check` reports vector mismatches via `testutil_checkfmt`.
- Uses `dcalloc` for an aligned zeroed buffer.

## Control Flow
`main` calls `run`. `run` allocates a 100-byte buffer, retrieves the CRC function, verifies CRCs for 1 to 4 zero bytes, then verifies `"123456789"` and `"The quick brown fox jumps over the lazy dog"`. It frees the buffer and exits.

## State and Persistence Behavior
No WiredTiger connection or persistent state is created. All state is in-memory test vectors.

## Dependencies and Integration Points
The test depends on the external checksum selector exported by WiredTiger and the test utility allocation/assertion layer. It complements WT-2695 by testing the public function pointer API rather than internal hardware/software functions.

## Risks and Test Signals
Any vector mismatch indicates wrong dispatch or CRC implementation. Coverage is intentionally small and does not test seeded or random inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4117_checksum/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4156_metadata_salvage/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt4156_metadata_salvage/main.c

## Purpose
WT-4156 tests metadata and turtle-file salvage after deliberate corruption. It creates many metadata entries, corrupts selected bytes in `WiredTiger.wt` and `WiredTiger.turtle`, verifies open behavior, opens with `salvage=true`, and checks salvaged metadata and table data.

## Important APIs, Types, and Functions
- Uses `TABLE_INFO` to describe expected objects and key/value formats.
- `byte_str` searches binary buffers for text despite embedded zeros.
- `create_data` creates tables/files with large `app_metadata` to spread metadata entries across pages.
- `corrupt_file` reads metadata/turtle files, replaces occurrences of a target URI string with `X`, and writes bytes back.
- `verify_metadata` walks the `metadata:` cursor and opens salvaged objects to verify data.
- `open_with_corruption`, `open_with_salvage`, and `open_normal` cover expected corruption, salvage, and post-salvage reopen paths.
- `copy_database` preserves database, metadata, and turtle snapshots for debugging.

## Control Flow
The test skips ASAN bypass and TSAN builds. It opens a clean home, creates several file and table objects plus one corrupt target, inserts one record into each, closes, and copies the database to `SAVE`. It corrupts `WiredTiger.wt`, saves that corrupt file, and runs corruption/salvage/normal verification. It then corrupts `WiredTiger.turtle`, saves the corrupt turtle, and repeats verification. Finally it removes the saved copy and cleans up.

## State and Persistence Behavior
Persistent state is central: many data files, `WiredTiger.wt`, `WiredTiger.turtle`, saved copies, `.CORRUPT` files, and `WiredTiger.wt.slvg` expected after salvage. The global `home`, `wt_session`, `test_abort`, and `test_out_of_sync` coordinate helper behavior.

## Dependencies and Integration Points
The test uses direct filesystem I/O, WiredTiger metadata cursor semantics, salvage open configuration, debug corruption mode, and `testutil_copy_ext`. It assumes metadata page size behavior through `APP_MD_SIZE`/`APP_BUF_SIZE`.

## Risks and Test Signals
Failure signals include missing corruption target string, unexpected open error, missing salvage file, salvaged corrupt object appearing when it should not, missing expected metadata entries, or data mismatch. Directly editing WiredTiger metadata makes the test sensitive to metadata encoding and file naming changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4156_metadata_salvage/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4333_handle_locks/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt4333_handle_locks/main.c

## Purpose
WT-4333 stress-tests data handle locking, cursor caching, verification, checkpoint handles, and file-manager sweeping under concurrent opens, reads, writes, and verifies.

## Important APIs, Types, and Functions
- Global state tracks `WT_CONNECTION *conn`, worker/verify counters, busy counters, URI list, home path, and `done`.
- `uri_init` creates up to 750 tables and loads 10,000 string keys per table, then checkpoints.
- `op` opens a random URI, sometimes at `checkpoint=WiredTigerCheckpoint`, performs read or write scans, and sometimes caches the cursor in a per-thread slot.
- `wthread` loops worker operations; `vthread` mixes operations with `session->verify`.
- `on_alarm` flips `done` after the run period.
- `sweep_stats` prints selected cursor/data-handle sweep statistics.
- `runone` configures file-manager aggressive close settings and runs worker/verify threads for 60 seconds.

## Control Flow
`main` skips on macOS and otherwise calls `run`. `run` parses local options, chooses a default home if needed, installs an alarm handler, and randomly selects five scenarios from a table covering different worker counts, URI counts, and cursor-cache settings. Each scenario recreates the home, opens WiredTiger, initializes data, launches workers plus one verifier, waits for the alarm-driven stop, reports counters, optionally prints sweep stats, and closes the connection.

## State and Persistence Behavior
Each scenario creates many tables with deterministic string key/value data and a checkpoint used for read-only checkpoint cursors. Runtime state includes cached cursors per thread and EBUSY retry counters. Unless `-p` is specified, the home is removed after all runs.

## Dependencies and Integration Points
The test relies on pthreads, signals, atomic counter helpers, statistics cursors, file manager configuration, checkpoint cursors, and verify. It uses custom command-line parsing instead of `TEST_OPTS`.

## Risks and Test Signals
Unexpected errors from cursor open/search/insert/verify fail the test. High `EBUSY` counters are informational. The test is time- and platform-sensitive, skipped on macOS due to historical hangs. It is stress-oriented and can be resource-heavy with 64 workers and hundreds of files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4333_handle_locks/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4891_meta_ckptlist_get_alloc/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt4891_meta_ckptlist_get_alloc/main.c

## Purpose
WT-4891 reproduces a metadata checkpoint-list allocation/verification path by keeping multiple checkpoint cursors open and then running `verify`.

## Important APIs, Types, and Functions
- Uses `CHECKPOINT_COUNT` set to 10.
- Uses `WT_CURSOR` for normal table updates and checkpoint cursors.
- Calls `session->checkpoint`, `session->open_cursor(..., "checkpoint=WiredTigerCheckpoint", ...)`, and `session->verify`.

## Control Flow
The test opens a clean home, creates a string-key/integer-value table, and opens a normal cursor. Ten times, it updates `key1` inside a snapshot transaction, checkpoints, and opens a checkpoint cursor to keep that checkpoint active. It closes the session, opens a new session, and verifies the table.

## State and Persistence Behavior
The same key is updated across ten checkpoints. Checkpoint cursors pin checkpoint metadata until the first session closes. The test is aimed at memory allocation behavior observable especially in sanitizer builds.

## Dependencies and Integration Points
It integrates with WiredTiger metadata checkpoint list retrieval and `__wt_verify` through the public `session->verify` entry point.

## Risks and Test Signals
Failures include verify errors or sanitizer-detected allocation misuse. The test does not inspect values; persistence correctness is inferred from successful checkpoint cursor handling and verify.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt4891_meta_ckptlist_get_alloc/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt6185_modify_ts/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt6185_modify_ts/main.c

## Purpose
WT-6185 verifies timestamped modify chains. It performs random modifies at increasing timestamps, rereads every committed version at its commit timestamp, and optionally forces eviction and checkpoints between operations.

## Important APIs, Types, and Functions
- Uses `WT_MODIFY`, `WT_RAND_STATE`, timestamped transactions, debug cursor eviction flags, and trace buffers.
- `modify_build` creates random modify vectors while preserving leading key-identifying bytes.
- `modify` performs up to four modifies in one transaction, optionally sets a read timestamp, commits at `ts + 1` or rolls back, and stores expected values in `list`.
- `repeat` rereads all committed expected values by `read_timestamp`.
- `evict` sets `WT_CURSTD_DEBUG_RESET_EVICT` around `cursor->reset` to force eviction.
- `trace_die` dumps operation history via `custom_die` on failure.

## Control Flow
The program parses local options for column-store mode, disabling checkpoint/eviction, preserving home, and RNG seed. It creates `file:xxx`, loads 101 records, closes/reopens, verifies a target record, and sets oldest timestamp to 1. For 250 runs, it resets trace state, performs 10 to 25 random modify operations on key 50, repeats historical reads after each operation, and randomly evicts or checkpoints depending on options. It prints one dot per run.

## State and Persistence Behavior
Persistent state includes one file with row or variable-length column keys. Timestamp state advances monotonically, with `oldest_timestamp=1`. The expected history list stores committed values and timestamps for the current run. Evictions and checkpoints force modify chains through reconciliation and disk state.

## Dependencies and Integration Points
The test depends on timestamp transactions, modify API, internal cursor debug eviction flags, and rollback/checkpoint behavior. The smoke wrapper runs both row and column modes.

## Risks and Test Signals
Any historical read mismatch triggers trace dumping. The random string length note documents a rare risk of exceeding trace buffer size. Options `-c` and `-e` can isolate checkpoint or eviction as failure contributors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt6185_modify_ts/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt6185_modify_ts/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/wt6185_modify_ts/smoke.sh

## Purpose
This smoke wrapper runs WT-6185 timestamped modify testing in row-store and variable-length column-store modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Resolves an optional binary argument or defaults to `$binary_dir/test_wt6185_modify_ts`.
- Uses `$TEST_WRAPPER`.

## Control Flow
The script invokes the binary once with default row-store behavior and once with `-C` for column-store mode.

## State and Persistence Behavior
The script creates no direct state. The binary creates timestamped WiredTiger files and removes them unless preserved.

## Dependencies and Integration Points
Assumes CMake-copied script location or explicit binary path. It maps csuite smoke coverage to both key formats.

## Risks and Test Signals
Any binary failure stops the script. Without extra options, checkpoint and eviction remain enabled in both modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt6185_modify_ts/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt6616_checkpoint_oldest_ts/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt6616_checkpoint_oldest_ts/main.c

## Purpose
WT-6616 validates recovery correctness for timestamped checkpoints after an unclean shutdown. A child workload inserts and deletes timestamped keys while checkpointing; the parent kills it, runs recovery, and verifies every key from recovered oldest to stable timestamp is visible at its own timestamp.

## Important APIs, Types, and Functions
- Uses `fork`, `kill(SIGKILL)`, `waitpid`, `sigaction`, pthread helpers, timestamps, sentinel files, and recovery config.
- `thread_ckpt_run` repeatedly runs `checkpoint(use_timestamp=true)`, queries `last_checkpoint`, and creates `checkpoint_done` after a checkpoint newer than `MAX_DATA`.
- `thread_run` inserts key X at timestamp X, advances stable to X, deletes at X+1, and advances oldest once data exceeds `MAX_DATA`.
- `run_workload` opens the child database, creates a non-logged table, and starts checkpoint and worker threads.
- Parent `main` waits for sentinel, sleeps a randomized or specified timeout, kills child, opens recovery, queries stable/oldest, and checks visibility.

## Control Flow
The program parses options for column-store mode, home, preserve, and timeout. Parent creates a clean home and forks. Child changes into the home, opens WiredTiger with logging enabled globally but creates the test table with `log=(enabled=false)`, starts checkpoint and worker threads, and waits forever. Parent waits for the first qualifying checkpoint, sleeps, kills the child, changes into the home, copies data for debugging, opens recovery, and scans timestamps from oldest through stable, starting a read-timestamp transaction for each.

## State and Persistence Behavior
The durable table is explicitly non-logged so timestamped history after recovery is meaningful. Stable and oldest timestamps are part of the persisted checkpoint state. The sentinel file coordinates parent timing. The parent may clean test artifacts and remove the home after verification.

## Dependencies and Integration Points
The test depends on process control, timestamped checkpoints, non-logged table recovery semantics, `testutil_copy_data`, and `TESTUTIL_ENV_CONFIG_REC`. The smoke wrapper runs row and column variants.

## Risks and Test Signals
Missing keys between oldest and stable after recovery signal data loss. A child exit before being killed is fatal. In `thread_run`, the remove path always calls `cursor->set_key(cursor, kname)` even when `use_columns` is true, unlike insertion and verification; that asymmetry is a notable column-mode risk. Runtime is timing-dependent and randomized unless `-t` is supplied.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt6616_checkpoint_oldest_ts/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt6616_checkpoint_oldest_ts/smoke.sh -->
# sources/storage-engines/wiredtiger/test/csuite/wt6616_checkpoint_oldest_ts/smoke.sh

## Purpose
This smoke wrapper runs WT-6616 checkpoint/oldest timestamp recovery testing in row and column modes.

## Important APIs, Types, and Functions
- POSIX shell with `set -e`.
- Resolves optional binary argument or `$binary_dir/test_wt6616_checkpoint_oldest_ts`.
- Uses `$TEST_WRAPPER`.

## Control Flow
The script runs the binary once with default row-store behavior and once with `-c` for column-store mode.

## State and Persistence Behavior
The script itself is stateless. The binary creates a child process, sentinel file, recovered database, and optional debug copy.

## Dependencies and Integration Points
It assumes build-tree placement or explicit binary path, and is part of csuite smoke coverage.

## Risks and Test Signals
Any failure in either mode stops the script. The binary has randomized duration unless overridden, so smoke runtime can vary.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt6616_checkpoint_oldest_ts/smoke.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt7989_compact_checkpoint/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt7989_compact_checkpoint/main.c

## Purpose
WT-7989 verifies that compaction and checkpoint can overlap without preventing compaction progress or leaving excessive reusable space. It runs stress and synchronized cases for row-store and column-store tables.

## Important APIs, Types, and Functions
- Uses `WT_CONNECTION`, `WT_SESSION`, pthreads, data-source statistics cursors, and timing stress.
- `run_test_clean` creates separate suffixed homes for stress/normal row/column cases.
- `populate` inserts one million records with large string payloads.
- `remove_records` deletes the middle third to create compactable space.
- `thread_func_compact` runs `session->compact`.
- `thread_func_checkpoint` runs three checkpoints with random sleeps.
- `thread_wait` synchronizes compact/checkpoint start in non-stress cases using an atomic counter.
- `get_compact_progress` and `check_db_size` assert compact stats and reusable-space percentage.

## Control Flow
`main` runs four scenarios: slow-checkpoint row, synchronized row, slow-checkpoint column, synchronized column. Each scenario recreates its home, opens a 2 GiB cache connection, optionally sets `WT_TIMING_STRESS_CHECKPOINT_SLOW` directly in the connection implementation, creates/populates/checkpoints a table, deletes one third of records, starts compact and checkpoint threads, waits for both, reads compact progress stats, checks file-size reuse percentage, and closes.

## State and Persistence Behavior
Each scenario persists a large table with one million records, then durable deletes and compaction rewrites blocks. Statistics counters for compact pages reviewed/skipped/rewritten and block reuse bytes are the main postcondition data.

## Dependencies and Integration Points
The test uses internal `WT_CONNECTION_IMPL` timing-stress flags, pthreads, statistics constants such as `WT_STAT_DSRC_BTREE_COMPACT_PAGES_REVIEWED`, and `TEST_OPTS` homes/URI. It is resource-heavy due to 2 GiB cache and large table volume.

## Risks and Test Signals
Assertions require pages reviewed and rewritten to be nonzero, and reusable space after compaction to be at most 20%. Timing and random checkpoint sleeps can make runtime variable. The test assumes compaction can make measurable progress after deleting the middle third.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt7989_compact_checkpoint/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt8057_compact_stress/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt8057_compact_stress/main.c

## Purpose
WT-8057 validates data consistency if compact is interrupted by an unclean shutdown. A child repeatedly mutates two identical tables while compacting only one; the parent kills the child and verifies both tables match after recovery.

## Important APIs, Types, and Functions
- Uses `fork`, `SIGKILL`, `sigaction`, `WT_EVENT_HANDLER`, compact event callbacks, statistics cursors, and recovery open.
- `handle_general` handles `WT_EVENT_COMPACT_CHECK` and periodically returns an error to interrupt compact.
- `workload_compact` creates two tables, populates both identically, checkpoints, removes identical key ranges, compacts `uri1`, logs compact stats, repopulates deleted records, and repeats.
- `verify_tables` and `verify_tables_helper` compare both directions across `table:compact1` and `table:compact2`.
- `log_db_size` and `get_compact_progress` report compaction behavior.

## Control Flow
`main` runs row and column tests. For each, parent creates a work directory and forks. The child opens WiredTiger, creates both tables, populates 100,000 records, enters up to 40 mutation/compact loops, and creates `checkpoint_done` after the first checkpoint. Parent waits for the sentinel, sleeps 40 seconds, kills the child, reopens the home with the same event handler and connection config, and verifies table equality.

## State and Persistence Behavior
Two tables are maintained as logical mirrors. Only the first is compacted, so recovery must preserve logical equality despite interrupted compaction and possible event-handler compact interruptions. The sentinel file gates parent timing.

## Dependencies and Integration Points
The test depends on process control, compact event callbacks, statistics, recovery, and row/column table configs. It integrates with the general event handler path through `WT_EVENT_COMPACT_CHECK`.

## Risks and Test Signals
Data mismatch, missing keys, child premature exit, or compact callback behavior not surfacing as an error when requested are failures. The child is expected not to finish naturally. The test is time- and IO-heavy.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt8057_compact_stress/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt8246_compact_rts_data_correctness/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt8246_compact_rts_data_correctness/main.c

## Purpose
WT-8246 verifies data correctness when foreground or background compaction is interrupted and recovery performs rollback-to-stable. It tests row and column stores across foreground/background compact modes.

## Important APIs, Types, and Functions
- Uses `fork`, `SIGKILL`, sentinel `compact_started`, timestamped transactions, recovery open, and foreground/background `session->compact`.
- Connection config enables `timing_stress_for_test=[compact_slow]` and `debug_mode=(background_compact)`.
- `workload_compact` populates data, performs timestamped full-table updates at 20/30/40/50, pins stable at 30, removes records at 60, checkpoints, then starts compact.
- `check` reads all records at a supplied timestamp and validates the visible string value.
- `large_updates` retries `WT_ROLLBACK` up to `MAX_RETRIES`.

## Control Flow
`main` runs four combinations of row/column and foreground/background. Each parent forks a child. Child creates the table, sets oldest/stable to 10, loads 800,000 records, checkpoints, updates all records through values A/B/C/D at timestamps 20/30/40/50, verifies them, sets stable to 30, removes a third at timestamp 60, checkpoints, and starts compact with `free_space_target=1MB`. Parent waits for the sentinel, sleeps briefly, kills child, opens recovery, and verifies timestamp reads: value A at 20 and value B at 30, 40, and 50 due to stable timestamp 30.

## State and Persistence Behavior
Timestamp history and stable timestamp are the core persistent state. Recovery should roll back updates newer than stable and preserve stable-visible data after interrupted compact. Foreground mode creates the sentinel before compact; background mode creates it after enabling background compaction and waits to let service work start.

## Dependencies and Integration Points
The test depends on RTS, background compaction debug mode, timing stress, process control, and nontrivial table volume. It uses `TESTUTIL_ENV_CONFIG_REC` for recovery open.

## Risks and Test Signals
Any missing record or wrong value at checked timestamps indicates compact/RTS correctness failure. It is resource-heavy and timing-sensitive. `large_updates` keeps `retry_attempts` across all records rather than resetting per key, which may make repeated rollbacks more likely to trip the global retry assertion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt8246_compact_rts_data_correctness/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt8963_insert_stress/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt8963_insert_stress/main.c

## Purpose
WT-8963 stresses concurrent random-key insert lists with many threads and large memory pages, then verifies the resulting table.

## Important APIs, Types, and Functions
- Uses `NUM_THREADS=110`, `THREAD_NUM_ITERATIONS=200000`, `KEY_MAX=UINT32_MAX`.
- Table config sets `memory_page_image_max=50MB` and row or column key format from `TEST_OPTS`.
- `thread_insert_race` opens its own session/cursor, waits on an atomic ready counter, and inserts random keys.
- `set_key` and `set_value` wrap variadic cursor calls for correct typing.

## Control Flow
The test parses options, defaults to 110 threads and row-store, opens a 4 GiB cache database, creates the table, starts all insert threads, joins them, closes/reopens the connection so verify can get exclusive access, verifies the table, scans all records to count them, prints count and duration, and cleans up.

## State and Persistence Behavior
The persistent table contains random unique or duplicate inserts depending on generated keys and WiredTiger semantics for the key format. The barrier ensures all threads begin inserting at roughly the same time, increasing insert-list contention.

## Dependencies and Integration Points
The test depends on pthreads, atomic operations, large cache availability, and `session->verify`. It lives in C suite because it needs validation overrides not available in the C++ suite according to the comment.

## Risks and Test Signals
Insert or verify failure indicates concurrency or insert-list corruption. Because keys are random, duplicate-key behavior affects final count. The workload is intentionally heavy: 22 million insert attempts with 110 threads and 4 GiB cache.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt8963_insert_stress/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt9199_checkpoint_txn_commit_race/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt9199_checkpoint_txn_commit_race/main.c

## Purpose
WT-9199 creates a race between a committing timestamped transaction and checkpoint stable timestamp selection. It verifies that a transaction whose commit timestamp becomes invalid relative to stable timestamp fails rather than being omitted from a checkpoint incorrectly.

## Important APIs, Types, and Functions
- Connection config enables `timing_stress_for_test=[commit_transaction_slow, prepare_checkpoint_delay]`.
- `thread_func_insert_txn` inserts 1000 records in one transaction, sets stable timestamp to 50, signals `inserted`, then attempts commit at stable+20 and expects `EINVAL`.
- `thread_func_checkpoint` waits for `inserted`, advances stable by 20, sleeps to let commit validate timestamp, checkpoints, and queries `last_checkpoint`.
- Shared globals: `global_stable_ts` and volatile `inserted`.

## Control Flow
`main` parses test options and calls `run_test`. `run_test` recreates the home, opens WiredTiger, creates the row-store table, starts insert and checkpoint threads, joins them, closes session and connection, and optionally removes the home.

## State and Persistence Behavior
The inserted records are part of a transaction expected to fail commit with `EINVAL`; durable user data is not the validation target. Persistent checkpoint timestamp state is queried to ensure checkpoint completed in the raced window.

## Dependencies and Integration Points
The test depends on timing-stress hooks for commit and checkpoint preparation, timestamp validation, pthread scheduling, and the C API transaction timestamp configuration.

## Risks and Test Signals
The central assertion is `commit_transaction` returning `EINVAL`. If the commit succeeds or returns a different error, the test fails. Thread coordination is intentionally minimal and timing-stress-driven, so behavior relies on the configured delays.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt9199_checkpoint_txn_commit_race/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt9937_parse_opts/main.c -->
# sources/storage-engines/wiredtiger/test/csuite/wt9937_parse_opts/main.c

## Purpose
WT-9937 unit-tests `testutil_parse_opts` and the extended parsing idiom using `testutil_parse_begin_opt`, `__wt_getopt`, `testutil_parse_single_opt`, and `testutil_parse_end_opt`.

## Important APIs, Types, and Functions
- Uses `TEST_OPTS` plus local `FICTIONAL_OPTS` and `SUBSET_TEST_OPTS`.
- `driver` contains simulated command lines and expected parsed fields.
- `check` chooses normal parsing when argv[0] is `parse_opts` and extended parsing when argv[0] is `parse_single_opt`.
- `verify_expect` compares actual options to expected values, with `NONZERO` used for generated seeds.
- `report` supports manual invocation output.

## Control Flow
With command-line arguments, the program expects `--parse_opts` or `--parse_single_opt`, rewrites argv[0] by skipping `--`, parses, reports changed fields, and cleans up. With no arguments, it iterates the driver table, builds expected `TEST_OPTS`, parses each synthetic command line, verifies expectations, and cleans up after each case.

## State and Persistence Behavior
No WiredTiger database state is created. Parser global state `__wt_optind` and `__wt_optreset` is reset before each simulated parse. `testutil_cleanup` is still called to release allocations in `TEST_OPTS`.

## Dependencies and Integration Points
The test targets shared test utility parsing, tiered-storage options (`-PT`, `-Po`, `-PS...`), build directory, thread count, verbose flag, and extended test-owned options.

## Risks and Test Signals
Failures reveal parser regressions in combined short options, attached/separate option values, tiered storage defaults, seed parsing, or handoff from test-owned options to testutil parsing. It intentionally verifies only a subset of `TEST_OPTS` fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/csuite/wt9937_parse_opts/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/ctest_dir_sync.cmake -->
# sources/storage-engines/wiredtiger/test/ctest_dir_sync.cmake

## Purpose
This CMake script synchronizes immediate files from a source directory to a destination directory for test runtime assets.

## Important APIs, Types, and Functions
- Requires `SYNC_DIR_SRC` and `SYNC_DIR_DST` variables.
- Uses `file(GLOB files ${SYNC_DIR_SRC}/*)` to enumerate entries.
- Uses `execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different ...)`.

## Control Flow
The script fails early if either required variable is missing. It globs all direct children in the source directory, extracts each basename, and copies each item to the destination path if different.

## State and Persistence Behavior
It writes/copies files under the destination directory. It is non-recursive as written and does not delete destination files that no longer exist in the source.

## Dependencies and Integration Points
`ctest_helpers.cmake` uses this script in `create_test_executable` for `ADDITIONAL_DIRECTORIES`, generating custom targets that keep test runtime directories synced into binary output directories.

## Risks and Test Signals
Missing variables are fatal. Because it uses a simple glob and `copy_if_different`, nested directories or deletions are not fully synchronized. Errors from `copy_if_different` surface through CMake process failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/ctest_dir_sync.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/ctest_helpers.cmake -->
# sources/storage-engines/wiredtiger/test/ctest_helpers.cmake

## Purpose
This file defines CMake helper functions for building WiredTiger C/C++ test executables and registering CTest tests or variants with consistent includes, libraries, runtime paths, copied assets, and labels.

## Important APIs, Types, and Functions
- `create_test_executable` creates a target, applies compiler diagnostics, include paths, linked libraries, optional output name/directory, optional copied files/directories, Darwin dSYM generation, platform RPATH, math library, Windows shim, and Antithesis voidstar linkage.
- `define_test_variants` expands `variant_name|variant args` entries into separate CTest tests with per-variant working directories and labels.
- `define_c_test` combines executable creation with CTest registration, optional exec script wrapping, dependency gating through `eval_dependency`, labels, and variants.

## Control Flow
Each function parses arguments with `cmake_parse_arguments` and emits fatal errors for unknown or missing required arguments. `create_test_executable` sets defaults, calls `add_executable`, configures target properties and platform-specific build/link behavior, then creates copy/sync custom targets for additional files/directories. `define_test_variants` creates working directories, separates variant args according to platform, and registers each test. `define_c_test` validates mutually exclusive `ARGUMENTS`/`VARIANTS`, checks dependencies, delegates executable creation, and either creates variants or a single `add_test`.

## State and Persistence Behavior
The helpers create build-system targets, copied runtime files, synced runtime directories, per-test working directories, and CTest metadata. Runtime output directories are set to current or caller-specified binary dirs.

## Dependencies and Integration Points
They depend on top-level variables and targets such as `wt::wiredtiger`, `test_util`, `COMPILER_DIAGNOSTIC_C_FLAGS`, `WT_LINUX`, `WT_DARWIN`, `WT_WIN`, `ENABLE_ANTITHESIS`, `CMAKE_SOURCE_DIR`, and `CMAKE_BINARY_DIR`. `define_c_test` integrates csuite labels `check;csuite` and supports script-based execution.

## Risks and Test Signals
Configuration-time fatal errors catch malformed helper use. In `define_c_test`, the variants path passes `CMDS ${test_cmd}` to `define_test_variants`, but the callee expects `CMD`; this looks like a potential typo that could leave custom commands unused for variants. Directory syncing is direct-child only because it delegates to `ctest_dir_sync.cmake`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/ctest_helpers.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cursor_order/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/cursor_order/CMakeLists.txt

## Purpose
This CMake file builds and registers the `test_cursor_order` executable and its row/variable-column variants.

## Important APIs, Types, and Functions
- Calls `create_test_executable(test_cursor_order SOURCES cursor_order_file.c cursor_order_ops.c cursor_order.c)`.
- Calls `define_test_variants` with variants `row|-tr` and `var|-tv`.
- Applies labels `check` and `test_cursor_order`.

## Control Flow
CMake first creates the executable target from the three cursor-order source files. It then registers two CTest variants that invoke the executable with row-store and variable-length column-store type arguments.

## State and Persistence Behavior
Build-system state includes the test executable target and two CTest entries with working directories generated by helper functions.

## Dependencies and Integration Points
The file depends on `ctest_helpers.cmake` functions being loaded by the parent CMake scope. It integrates the cursor order test into the check smoke set.

## Risks and Test Signals
Build failures would point to helper availability or source compilation errors. Runtime failures are surfaced by the generated `test_cursor_order_row` or `test_cursor_order_var` CTest entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cursor_order/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cursor_order/cursor_order.c -->
# sources/storage-engines/wiredtiger/test/cursor_order/cursor_order.c

## Purpose
This is the main driver for the cursor-order stress test. It runs append inserter and reverse scanner workloads to validate cursor ordering for row-store and variable-length column-store files.

## Important APIs, Types, and Functions
- Uses `SHARED_CONFIG` from `cursor_order.h`.
- Parses local options for connection config, multiple files, home, key count, log file, operation counts, scanner/writer counts, run count, file type, and workload variation.
- `wt_connect` recreates the home and opens WiredTiger with statistics logging and optional caller config.
- `wt_shutdown` checkpoints and closes the connection.
- `shutdown` removes the work directory.
- Event handlers route errors to stderr and messages to a log file or stdout.

## Control Flow
`main` initializes default shared config, parses options, validates that varying operation counts require multiple files, installs SIGINT cleanup, then loops for the requested number of runs. Each run removes prior home state, opens a connection, calls `ops_start(cfg)` to perform the workload, and checkpoints/closes. Run count `0` means continuous.

## State and Persistence Behavior
Each run creates a fresh WiredTiger home, loads/operates on files through helper modules, checkpoints at shutdown, and removes the home at the start of the next run or on interrupt. Optional log file captures WiredTiger messages.

## Dependencies and Integration Points
The driver depends on `load`, `ops_start`, and `verify` functions from sibling files. It integrates with CTest variants through `-tr` and `-tv`. It uses `testutil_work_dir_from_path` and direct `__wt_getopt` parsing.

## Risks and Test Signals
Failures surface through testutil assertions, invalid option usage, or workload helper errors. Infinite runs are possible with `-r 0`, so smoke variants use defaults. Interrupt cleanup removes the home and exits failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cursor_order/cursor_order.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cursor_order/cursor_order.h -->
# sources/storage-engines/wiredtiger/test/cursor_order/cursor_order.h

## Purpose
This header defines shared types and function declarations for the cursor-order test.

## Important APIs, Types, and Functions
- Includes `test_util.h` and `<signal.h>`.
- Defines `FNAME "file:cursor_order.%03d"` for generated file URIs.
- Defines `enum __ftype { ROW, VAR }`.
- Defines `SHARED_CONFIG`, holding connection pointer, file type, key range, operation counts, thread counts, multiple-file/vary flags, and finish flag.
- Declares `load`, `ops_start`, and `verify`.

## Control Flow
The header has no executable control flow. It establishes the contract shared by the main driver, file loader/verifier, and operation workload implementation.

## State and Persistence Behavior
`SHARED_CONFIG` is the in-memory state container passed between modules. `key_range` tracks current append range; `thread_finish` signals worker shutdown; `conn` carries the active WiredTiger connection.

## Dependencies and Integration Points
It is included by `cursor_order.c`, `cursor_order_file.c`, and the operations source. The `FNAME` pattern aligns multiple-file workload naming across modules.

## Risks and Test Signals
Mismanaging shared fields can affect thread coordination and generated URI consistency. Since this is a header, direct test signals come from consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cursor_order/cursor_order.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cursor_order/cursor_order_file.c -->
# sources/storage-engines/wiredtiger/test/cursor_order/cursor_order_file.c

## Purpose
This file provides table/file creation, initial bulk loading, and verification helpers for the cursor-order test.

## Important APIs, Types, and Functions
- `file_create` creates a WiredTiger file with row or record-number key format, tuned page sizes, and `split_deepen_min_child=200`.
- `load` creates the file, opens a bulk cursor, inserts `cfg->nkeys` ordered records, sets `cfg->key_range`, closes the cursor, checkpoints, and closes the session.
- `verify` opens a session and calls `testutil_verify`.

## Control Flow
`load` calls `file_create`, opens a bulk cursor, iterates keys from 1 through `nkeys`, formats row keys as zero-padded strings or column keys as recnos, stores a formatted `WT_ITEM` value, inserts, checkpoints, and returns. `verify` is a simple wrapper around WiredTiger verification.

## State and Persistence Behavior
The loaded file is persistent and checkpointed before workload threads run. `cfg->key_range` records the highest loaded key so append workloads know where to continue.

## Dependencies and Integration Points
The file depends on `SHARED_CONFIG`, active `WT_CONNECTION`, `WT_SESSION`, bulk cursor semantics, and `testutil_verify`. It is called by the cursor-order operations module and driver.

## Risks and Test Signals
Create tolerates `EEXIST`; other create, bulk insert, checkpoint, or verify errors fail. Bulk loading assumes ordered keys and correct key type for row versus variable-column mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/cursor_order/cursor_order_file.c -->
