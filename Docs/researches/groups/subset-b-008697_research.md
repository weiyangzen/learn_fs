<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_bench_tool_test.cc -->
# sources/storage-engines/rocksdb/tools/db_bench_tool_test.cc

## Purpose
This file is a GoogleTest suite for the `db_bench` tool's `--options_file` handling. It verifies that `db_bench_tool()` can open RocksDB using persisted or hand-written OPTIONS files, run a small `fillseq` benchmark, and leave the created database with DB and column-family options matching the expected sanitized options.

## Important APIs, Types, and Functions
- `DBBenchTest` is the test fixture. It owns per-thread test paths, a synthetic argv buffer, and helpers for invoking `db_bench_tool()` in-process.
- `ResetArgs()` and `AppendArgs()` maintain a bounded `argc`/`argv` array backed by `arg_buffer_`, avoiding shell execution while still exercising the CLI parser.
- `GetDefaultOptions()` mirrors the options that `db_bench` overrides from RocksDB defaults, then calls `SanitizeOptions(db_path_, opt)`.
- `RunDbBench()` appends fixed benchmark arguments plus `--db`, `--wal_dir`, and `--options_file`, then expects `db_bench_tool(argc(), argv()) == 0`.
- `VerifyOptions()` loads the latest persisted options from the resulting DB with `LoadLatestOptions()` and verifies exact DB and CF option matches using `RocksDBOptionsParser::VerifyDBOptions()` and `VerifyCFOptions()`.
- `options_file_content` embeds an older-style OPTIONS file string to test compatibility with `LoadOptionsFromFile()`.

## Control Flow
The fixture creates `test_path_`, `db_path_`, and `wal_path_` in its constructor. Each test writes or loads an OPTIONS file, adjusts expectations for options not consumed from file by `db_bench` such as `wal_dir`, runs a one-thousand-key fill benchmark, and then verifies the DB's OPTIONS files against the expected configuration. The tests cover default leveled compaction, universal compaction with one level, universal compaction with twelve levels, and loading a complete options string from a file before running the benchmark.

## State and Persistence Behavior
The test persists OPTIONS files via `PersistRocksDBOptions()` or writes raw `options_file_content` through `Env::NewWritableFile()`. It then relies on `db_bench` creating a real DB and writing current OPTIONS metadata under `db_path_`. The WAL path is separate (`wal_path_`) and must be reflected in the expected `Options`. Cleanup is intentionally disabled in the destructor, which can leave test DB artifacts for debugging.

## Dependencies and Integration Points
This file depends on gflags, GoogleTest, `rocksdb/db_bench_tool.h`, options parser utilities, RocksDB DB implementation sanitization, `test_util`, and `util/random`. The whole test is compiled only under `GFLAGS`; otherwise `main()` prints a skip message. It exercises the same in-process entry point used by the `db_bench` binary, so parser and default-option drift are visible.

## Risks and Edge Cases
- `AppendArgs()` stores pointers into a fixed 100 KB buffer; newly added arguments can trip buffer assertions.
- Exact option verification is intentionally brittle. Any legitimate default or sanitization change in `db_bench`, DB open, table options, or OPTIONS file parsing must update `GetDefaultOptions()` or the embedded file.
- The negative checks against default `DBOptions()` and `ColumnFamilyOptions()` ensure the test is not passing through an unverified default DB, but also make default changes noisy.
- The `OptionsFileFromFile` fixture uses a historical options format and may need updates as obsolete options are removed or renamed.

## Test Signals
The direct signals are four `TEST_F(DBBenchTest, ...)` cases and the gflags-gated `main()`. Passing tests confirm that `db_bench` consumes OPTIONS files, persists compatible current options, and rejects exact comparison against plain defaults.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_bench_tool_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_crashtest.py -->
# sources/storage-engines/rocksdb/tools/db_crashtest.py

## Purpose
`db_crashtest.py` orchestrates repeated `db_stress` runs for RocksDB crash consistency testing. It randomizes a very large option surface, sanitizes incompatible combinations, runs blackbox tests by externally terminating `db_stress`, runs whitebox tests with internal kill points and compaction-mode rotation, verifies final DB consistency, emits diagnostics, and cleans up DB and expected-value state after success.

## Important APIs, Types, and Functions
- Global option maps: `default_params`, `blackbox_default_params`, `whitebox_default_params`, `simple_default_params`, `cf_consistency_params`, `txn_params`, `optimistic_txn_params`, `best_efforts_recovery_params`, `blob_params`, `blob_direct_write_*_params`, `ts_params`, `tiered_params`, and `multiops_txn_params`.
- `early_argument_parsing_before_main()` parses seed overrides before global random defaults are evaluated and detects remote DB mode from `--env_uri` or `--fs_uri`.
- `apply_random_seed_per_iteration()` reseeds every run, preserving reproducibility when requested.
- `stress_cmd_env()` injects `TSAN_OPTIONS=suppressions=.../tsan_suppressions.txt` only when the caller has not already supplied TSAN settings.
- `get_db_parent_dir()`, `get_ev_parent_dir()`, and `setup_multiops_txn_key_spaces_file()` allocate DB, expected-value, and transaction key-space paths while respecting `TEST_TMPDIR`, `TEST_TMPDIR_EXPECTED`, and remote DB constraints.
- `is_direct_io_supported()` probes local direct I/O support before leaving direct I/O flags enabled.
- `finalize_and_sanitize()` evaluates callable random values and applies the core compatibility matrix across WAL, blob direct write, direct I/O, timestamps, transactions, remote compaction, user-defined indexes, multiscan, cache tiering, compaction styles, fault injection, and multi-DB mode.
- `gen_cmd_params()` merges defaults, selected modes, and parsed CLI overrides by documented priority.
- `gen_cmd()` creates the sorted `db_stress` command line, creates expected-value directories, and returns both command and finalized parameters.
- Diagnostic helpers include `human_readable_bytes()`, `output_matches_no_space()`, `collect_diagnostic_roots()`, `format_filesystem_usage()`, `collect_directory_usage()`, and `build_out_of_space_diagnostics()`.
- Process helpers include `execute_cmd()`, `strip_expected_sigterm_stderr()`, `cleanup_after_success()`, and `print_and_cleanup_fault_injection_log()`.
- Entrypoints are `blackbox_crash_main()`, `whitebox_crash_main()`, and `main()`.

## Control Flow
Module import immediately runs early seed parsing and initializes randomized defaults. `main()` builds an argparse parser from the union of known parameter maps, parses remaining arguments, validates local `TEST_TMPDIR`, optionally overrides `stress_cmd`, and dispatches by `test_type`.

In blackbox mode, the script builds a persistent DB and expected-values directory, loops until `duration`, reseeds every iteration, generates a sanitized command, starts `db_stress`, waits `interval`, terminates it on timeout, filters narrow expected post-SIGTERM io_uring stderr, fails on unexpected early exit or stderr, and resets `destroy_db_initially` after the first run. After the loop it runs one final `verification_only=1` pass with `skip_verifydb=0` and `verify_timeout`, then destroys the DB through `db_stress --destroy_db_and_exit`.

In whitebox mode, the script loops until `duration` and rotates `check_mode`: kill-point stress, universal compaction, FIFO compaction, and normal operation. Kill mode also rotates through different `kill_exclude_prefixes` and odds to hit different write-path regions. When compaction style changes after the halfway mark, it sets `destroy_db_initially=1` to avoid reusing incompatible DB state. Each run must either die as expected when kill testing or return zero in non-kill runs. Completion or timeout triggers cleanup.

## State and Persistence Behavior
Persistent state is split between the RocksDB DB path and local expected-values state. The DB path may use a local or remote Env and is created/destroyed by C++ `db_stress`; expected values are always managed by Python on the local filesystem. Multi-DB mode creates `db_0`, `db_1`, etc. under the expected-values parent. The script stores global `ev_parent_dir_global` and `multiops_txn_key_spaces_file` so temporary artifacts can be removed at the end. Fault-injection logs are discovered in `TEST_TMPDIR` or `/tmp` by PID and printed in bounded tail form.

## Dependencies and Integration Points
The main external binary is `./db_stress`, configurable via `--stress_cmd`. Cleanup also uses that binary with `--destroy_db_and_exit=1` so it uses the same RocksDB Env and URI flags. The script relies on Python stdlib modules only, but it is tightly coupled to the `db_stress` flag set and RocksDB feature compatibility. It integrates with TSAN suppressions, `TEST_TMPDIR`, `TEST_TMPDIR_EXPECTED`, `DEBUG_LEVEL`, optional `pstack`, remote filesystem flags, and Linux direct-I/O behavior.

## Risks and Edge Cases
- The compatibility matrix is large and order-sensitive. Later sanitizers can override earlier command-line choices, so adding a new feature flag requires reasoning about every interacting mode.
- Import-time randomization means tests that import this module must control `sys.argv` and seeds before execution.
- Blackbox mode treats timeout as expected, but unexpected stderr after SIGTERM fails unless filtered by `_IGNORED_SIGTERM_STDERR_RE`. The filter is deliberately narrow to avoid hiding real io_uring failures.
- Remote DB mode disables features whose local-file visibility assumptions do not hold, especially blob direct write and direct I/O.
- `gen_cmd()` sorts flags for reproducibility, but unknown args pass through unsanitized.
- Out-of-space diagnostics parse absolute paths from output. This is useful in CI but can be expensive on very large directory trees.
- `whitebox_crash_main()` treats long timeout as acceptable cleanup territory, so callers must inspect surrounding output for hangs versus true success.

## Test Signals
The companion `db_crashtest_test.py` unit tests exercise TSAN environment handling, expected-values directory preservation, sanitization for WAL-disabled, blob direct write, range-conversion, and multi-DB modes, SIGTERM stderr filtering, no-space detection, suffix accounting, and out-of-space diagnostics. The broader integration signal is successful blackbox or whitebox crash-test execution with final verification and cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_crashtest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_crashtest_test.py -->
# sources/storage-engines/rocksdb/tools/db_crashtest_test.py

## Purpose
This Python unit test file validates selected behavior in `db_crashtest.py` without running `db_stress`. It focuses on import safety, environment handling, parameter sanitization, SIGTERM stderr filtering, out-of-space detection, directory usage diagnostics, and multi-DB flag compatibility.

## Important APIs, Types, and Functions
- `load_db_crashtest_module()` imports `db_crashtest.py` under the synthetic module name `db_crashtest_under_test` while temporarily replacing `sys.argv` with only the script path. This isolates import-time argparse and random seeding.
- `DBCrashTestTest.setUp()` creates a temporary `TEST_TMPDIR`, clears `TEST_TMPDIR_EXPECTED`, and records old environment values.
- `tearDown()` restores `TEST_TMPDIR`, `TEST_TMPDIR_EXPECTED`, and `TSAN_OPTIONS`, then deletes the temp tree.
- `build_params()` copies a parameter map, injects the temp DB path, and applies test-specific overrides.

## Control Flow
Each test imports a fresh copy of `db_crashtest.py`, calls one helper or sanitizer, and asserts exact outputs. Environment-sensitive tests control `TSAN_OPTIONS` and temp-directory variables before import. Sanitization tests build representative parameter maps and verify only the relevant incompatible flags change. Diagnostic tests create a small filesystem tree, synthesize no-space stderr, and assert that generated diagnostic text contains aggregate and per-directory suffix summaries.

## State and Persistence Behavior
The test owns all filesystem state under a per-test temp directory. It explicitly checks that `get_ev_parent_dir()` does not remove existing expected-value contents. Out-of-space diagnostics create small marker files such as `CURRENT`, `.sst.trash`, and `.sst` to validate byte and suffix reporting. No RocksDB database is opened and no `db_stress` subprocess is started.

## Dependencies and Integration Points
The suite uses `unittest`, `importlib.util`, `tempfile`, `shutil`, and environment variables. It integrates directly with `db_crashtest.py` internals instead of a public CLI, so it is sensitive to function names and import-time side effects. The tests are designed to be run from the `tools` directory or any context where the relative `db_crashtest.py` path resolves.

## Risks and Edge Cases
- Since `db_crashtest.py` runs early parsing during import, test isolation depends on the temporary `sys.argv` replacement.
- These tests cover targeted invariants, not the full sanitizer matrix. Large portions of option interactions remain validated only by integration crash tests.
- Exact diagnostic string assertions can become brittle if formatting changes.
- Environment restoration in `tearDown()` is essential because TSAN and temp-dir variables influence later tests in the same process.

## Test Signals
The tests assert that default TSAN suppressions are added only when appropriate, expected-value directories are preserved, WAL-disabled and blob-direct-write modes disable batch/snapshot testing, range tombstone conversion disables SQFC range queries, SIGTERM stderr filtering hides only known retryable post-termination messages, no-space messages are detected, suffix extraction preserves compound suffixes, multi-DB mode disables unsupported operations, and diagnostics summarize local file usage.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_crashtest_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_repl_stress.cc -->
# sources/storage-engines/rocksdb/tools/db_repl_stress.cc

## Purpose
`db_repl_stress.cc` stress-tests RocksDB replication log iteration by writing random data on a background thread while the main thread continuously consumes updates through `DB::GetUpdatesSince()`. It verifies that transaction-log batches are observed in contiguous sequence-number order and that no extra or missing updates appear.

## Important APIs, Types, and Functions
- gflags: `--num_inserts`, `--wal_ttl_seconds`, and `--wal_size_limit_MB`.
- `DataPumpThread` carries an already-opened `DB*` to the writer thread.
- `DataPumpThreadBody()` writes `FLAGS_num_inserts` random 500-byte keys and values using `DB::Put()`.
- `main()` configures WAL retention options, creates a fresh DB, starts the writer thread with `Env::StartThread()`, and repeatedly opens `TransactionLogIterator` instances with `GetUpdatesSince(currentSeqNum, &iter)`.
- `BatchResult.sequence` is compared to the expected `currentSeqNum`.

## Control Flow
After parsing flags, the program builds a test DB path from `Env::GetTestDirectory()`, destroys any previous DB, opens a new DB, and starts the writer. The main loop repeatedly tries `GetUpdatesSince()`. If the API cannot provide an iterator, it probes until either enough updates have already been read or a new iterator becomes available. When the iterator is valid, it walks batches, incrementing both `num_read` and `currentSeqNum`. Success is declared after all expected inserts have been read and subsequent probing cannot find more updates.

## State and Persistence Behavior
The program writes a real RocksDB database and WAL files under the environment's test directory. WAL retention is governed by `WAL_ttl_seconds` and `WAL_size_limit_MB`. The DB is destroyed before opening but is not explicitly destroyed after success. Sequence state is in-memory only; the persistence behavior under test is WAL availability to transaction-log iteration.

## Dependencies and Integration Points
The file depends on gflags, `rocksdb/db.h`, transaction log iterator APIs, `db/write_batch_internal.h`, `test_util/testutil.h`, and RocksDB's `Env` thread launcher. Without gflags it builds a small `main()` that asks the user to install gflags and returns failure.

## Risks and Edge Cases
- The writer thread is not joined. The main thread exits once it has read all expected updates, relying on process termination for cleanup.
- Random keys can collide in theory, but sequence-number checks are independent of key uniqueness.
- WAL TTL or size settings that remove logs too aggressively can cause repeated `GetUpdatesSince()` failures before all updates are read.
- The program assumes one write batch per `Put()` and increments expected sequence by one per batch.

## Test Signals
The signal is process exit status and stderr messages. It prints "Successful!" and returns zero when exactly `num_inserts` ordered updates are observed; it exits nonzero on open failure, write failure, missed sequence numbers, or too many updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_repl_stress.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_sanity_test.cc -->
# sources/storage-engines/rocksdb/tools/db_sanity_test.cc

## Purpose
`db_sanity_test.cc` is a standalone create/verify utility that builds small RocksDB databases under multiple option configurations and later verifies that they can be reopened and read correctly. It is aimed at broad sanity coverage of table factories, comparators, filters, and compression variants.

## Important APIs, Types, and Functions
- `SanityTest` is the abstract base. It stores a root path, defines `Name()` and `GetOptions()`, and implements `Create()` and `Verify()`.
- `SanityTest::Create()` destroys any old named DB, opens with `create_if_missing`, writes one million `keyN -> valueN` records, and flushes.
- `SanityTest::Verify()` reopens with the same options and reads back all one million keys.
- Derived classes configure specific options: `SanityTestBasic`, `SanityTestSpecialComparator`, `SanityTestZlibCompression`, `SanityTestZlibCompressionVersion2`, `SanityTestLZ4Compression`, `SanityTestLZ4HCCompression`, `SanityTestZSTDCompression`, `SanityTestPlainTableFactory`, and `SanityTestBloomFilter`.
- `RunSanityTests(command, path)` allocates the test set, dispatches to `Create()` or `Verify()`, reports status, deletes each object, and returns aggregate success.

## Control Flow
`main()` expects `<path> [create|verify]`, normalizes the path to end in `/`, and calls `RunSanityTests()`. For `create`, each derived test destroys and recreates its own database directory named by `path + Name()`. For `verify`, each test opens its existing database and validates every key/value pair. The test list is suppressed under `__clang_analyzer__` to avoid false positives.

## State and Persistence Behavior
Each option profile maps to a separate physical RocksDB directory. The utility writes one million records and flushes them, leaving persisted SST and metadata for later verification. Comparator and table factory settings must be identical between create and verify, because RocksDB requires matching comparator/table behavior to read existing files.

## Dependencies and Integration Points
The file uses core RocksDB DB APIs, `Env`, comparators, compression enum values, block-based and plain table factories, prefix transforms, Bloom filters, and `Status`. It integrates as a command-line tool rather than a gtest. It references version macros for block-based table `format_version = 2` compatibility.

## Risks and Edge Cases
- Compression profiles require their corresponding compression libraries; missing libraries can make create fail.
- The special comparator is manually allocated and deleted; ownership is simple but not RAII.
- PlainTable requires a prefix extractor and mmap reads, so filesystem and platform behavior can affect it.
- Writing one million keys per profile is intentionally heavy for a sanity tool and may be slow or disk-intensive.
- Path concatenation depends on `main()` appending a slash.

## Test Signals
The program prints each profile name and `Status::ToString()` result. Exit code zero means all profiles succeeded; exit code one means at least one create or verify operation failed. A corruption status in `Verify()` pinpoints key/value mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_sanity_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dbench_monitor -->
# sources/storage-engines/rocksdb/tools/dbench_monitor

## Purpose
`dbench_monitor` is a Bash wrapper that launches `db_bench` with configurable defaults and monitors its process resource usage through the companion `pflag` script. The documented default intent is virtual-memory-size monitoring during a `readwhilewriting` benchmark.

## Important APIs, Types, and Functions
- Environment-controlled parameters include `bs`, `ztype`, `benches`, `reads`, `threads`, `cs`, `vsize`, `comp`, and `num`.
- `usage()` prints the accepted `-h` help text and explains environment overrides.
- `DB_BENCH` is resolved as `$DIR/../db_bench`; `PFLAG` is `$DIR/pflag`.
- A trap removes the temporary log and kills the benchmark PID on signals 1, 2, 3, and 15.

## Control Flow
The script verifies that `db_bench` exists and is executable, handles `-h`, installs the cleanup trap, creates `/tmp/dbench_monitor.$$`, applies default parameter values, prints the command in debug mode, starts `db_bench` in the background with stdout/stderr redirected to the log, captures `PID`, and invokes `${PFLAG} -p $PID -v` to monitor the process. After monitoring finishes it removes the log.

## State and Persistence Behavior
The only script-owned file is a temporary log in `/tmp`, removed on normal exit and trapped interrupts. The underlying `db_bench --use_existing_db` may create or reuse RocksDB data under its own default DB path and can leave LOCK files if killed, as noted in comments. The monitor does not manage DB cleanup.

## Dependencies and Integration Points
This wrapper depends on Bash, an executable `db_bench` adjacent to the tools layout, and `tools/pflag`. It integrates with `db_bench` CLI flags and whatever monitoring modes `pflag` supports. The script is intended to be run from the RocksDB build tree where `../db_bench` exists relative to `tools`.

## Risks and Edge Cases
- The script calls `warn` on launch failure, but no `warn` function is defined.
- Variables are mostly unquoted, so spaces in paths or environment values can break command execution.
- The temporary log name is predictable by PID and stored in `/tmp`.
- The trap calls `kill ${PID}` even if `PID` has not been set yet.
- `exit -1` is non-portable in meaning, though Bash maps it to an unsigned exit status.

## Test Signals
There is no formal test. Operational signals are successful `db_bench` launch, `pflag` output, the debug command line, and cleanup of the `/tmp/dbench_monitor.$$` log.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dbench_monitor -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/db_dump_tool.cc -->
# sources/storage-engines/rocksdb/tools/dump/db_dump_tool.cc

## Purpose
This file implements the binary dump and undump logic behind RocksDB's `rocksdb_dump` and `rocksdb_undump` tools. It serializes a read-only DB into a simple stream format and reconstructs a DB by reading that format and writing each key/value pair.

## Important APIs, Types, and Functions
- `DbDumpTool::Run(const DumpOptions&, Options)` opens a DB read-only and writes a dump file.
- `DbUndumpTool::Run(const UndumpOptions&, Options)` opens a dump file, validates it, opens or creates a DB, writes records, and optionally compacts.
- Dump format constants are `magicstr = "ROCKDUMP"` and an eight-byte version `{0,0,0,0,0,0,0,1}`.
- `EncodeFixed32()` and `DecodeFixed32()` serialize metadata length, key length, and value length.
- `Env::NewWritableFile()`, `Env::NewSequentialFile()`, `WritableFile::Append()`, `SequentialFile::Read()`, and `SequentialFile::Skip()` perform file I/O.

## Control Flow
Dumping opens the source DB with `create_if_missing=false`, opens the destination file, appends magic and version, emits either `{}` for anonymous dumps or JSON-like metadata containing absolute DB path, hostname, and creation time, then iterates the DB from first key to last. Each record is `uint32 key_size`, key bytes, `uint32 value_size`, and value bytes.

Undumping opens the sequential dump file, reads and validates magic and version, reads the info blob size and skips the metadata, opens the destination DB with `create_if_missing=true`, then loops reading key-size fields. A short or failed read of the next key-size ends the loop; short reads for key data, value size, or value data are treated as errors. Scratch buffers grow by doubling to accommodate large keys or values. Each record is inserted with `DB::Put()`. If requested, it compacts the full DB.

## State and Persistence Behavior
The dump file persists all key/value pairs visible through a default iterator in sorted order, plus optional metadata. It does not encode column families, snapshots, timestamps, sequence numbers, merges, deletes, range tombstones, blob-file identity, or DB options. Undump writes records into a live RocksDB DB path using caller-supplied options and can compact after loading.

## Dependencies and Integration Points
This implementation depends on `rocksdb/db_dump_tool.h` declarations, core `DB` and `Env` APIs, and RocksDB fixed-width coding helpers. It is invoked by the wrapper binaries in `rocksdb_dump.cc` and `rocksdb_undump.cc`, which parse gflags and options strings.

## Risks and Edge Cases
- Metadata JSON is built with `snprintf()` and does not escape strings; unusual path or hostname characters can produce invalid JSON-like text.
- The dump format has no checksum and limited validation. Truncation at a key-size boundary is treated as normal end-of-file.
- `DbDumpTool::Run()` checks iterator failure but prints `status.ToString()` instead of `it->status()`, so the reported status can be stale.
- Only the default column family is represented.
- Lengths are 32-bit; very large keys or values beyond that format are unsupported.

## Test Signals
There is no local unit test in this file. Signals are boolean return values, stderr messages on open/read/write/iteration/compaction failures, and successful round-trip use through `rocksdb_dump` and `rocksdb_undump`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/db_dump_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/rocksdb_dump.cc -->
# sources/storage-engines/rocksdb/tools/dump/rocksdb_dump.cc

## Purpose
`rocksdb_dump.cc` is the command-line frontend for `DbDumpTool`. It parses dump flags, optionally parses a RocksDB options string, and writes a binary dump of a DB.

## Important APIs, Types, and Functions
- gflags: `--db_path`, `--dump_location`, `--anonymous`, and `--db_options`.
- `GetOptionsFromString()` parses `--db_options` into a `Options` object.
- `DumpOptions` carries `db_path`, `dump_location`, and `anonymous` to `DbDumpTool::Run()`.
- The gflags-disabled fallback `main()` prints an installation error and returns failure.

## Control Flow
Under gflags, `main()` parses command-line flags, requires both `--db_path` and `--dump_location`, fills `DumpOptions`, parses `--db_options` if supplied, runs `DbDumpTool`, and maps a false return to exit code one.

## State and Persistence Behavior
This wrapper does not manage DB state directly. It reads the source DB through `DbDumpTool` and creates or overwrites the dump file at `--dump_location` according to the underlying `Env::NewWritableFile()` behavior. With `--anonymous`, metadata about the host, time, and absolute DB path is omitted from the dump.

## Dependencies and Integration Points
The file depends on gflags compatibility wrappers, `rocksdb/convenience.h`, and `rocksdb/db_dump_tool.h`. It integrates the reusable dump implementation with shell users and build targets.

## Risks and Edge Cases
- It validates only presence of paths. Existence, readability, and writeability errors are deferred to `DbDumpTool`.
- Options parsing starts from default `Options`; callers must supply enough options to open DBs that require custom comparators or table factories expressible as option strings.
- The typo-like help text for `dump_location` does not affect behavior.

## Test Signals
Exit code zero indicates successful dump. Exit code one indicates missing required flags, options-string parse failure, or a `DbDumpTool` failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/rocksdb_dump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/rocksdb_undump.cc -->
# sources/storage-engines/rocksdb/tools/dump/rocksdb_undump.cc

## Purpose
`rocksdb_undump.cc` is the command-line frontend for `DbUndumpTool`. It parses source dump and destination DB paths, optional compaction, and optional RocksDB open options, then loads dump records into a DB.

## Important APIs, Types, and Functions
- gflags: `--dump_location`, `--db_path`, `--compact`, and `--db_options`.
- `GetOptionsFromString()` parses DB options.
- `UndumpOptions` carries `db_path`, `dump_location`, and `compact_db`.
- `DbUndumpTool::Run()` performs the actual format validation, record reads, writes, and optional compaction.

## Control Flow
Under gflags, `main()` parses flags, requires both `--db_path` and `--dump_location`, populates `UndumpOptions`, parses `--db_options` if present, invokes `DbUndumpTool`, and returns one on failure. Without gflags, it builds a fallback executable that reports the missing dependency.

## State and Persistence Behavior
The wrapper causes records from the dump file to be written into the DB at `--db_path`; the underlying implementation opens the DB with `create_if_missing=true`. It does not destroy any existing DB, so loading into a populated DB can overwrite matching keys and leave unrelated keys intact. `--compact` triggers full-range compaction after load.

## Dependencies and Integration Points
This file depends on the same gflags and options-string utilities as `rocksdb_dump.cc` and integrates shell usage with `DbUndumpTool`.

## Risks and Edge Cases
- Existing destination DB contents are not cleared.
- Custom DBs requiring non-string-parseable factories may not be openable through `--db_options`.
- Input format validation and truncation behavior are owned by `DbUndumpTool`, not the wrapper.

## Test Signals
Exit code zero means all records were loaded and optional compaction succeeded. Exit code one means missing flags, parse failure, invalid dump input, DB write/open failure, or compaction failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/dump/rocksdb_undump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/generate_random_db.sh -->
# sources/storage-engines/rocksdb/tools/generate_random_db.sh

## Purpose
This Bash script loads pre-generated text data into a RocksDB database using the `ldb load` command while varying compression settings and optionally adding deterministic range tombstones or point deletes. It is used to generate DBs with mixed feature coverage for compatibility and testing.

## Important APIs, Types, and Functions
- Positional arguments are `<input_data_path> <DB Path> [<ldb_command>]`.
- `ldb_cmd` defaults to `./ldb`.
- Feature probes use `ldb --version`, a trial `ldb load --compression_type=mixed`, and `ldb --help | grep deleterange`.
- `compression_opts` starts with `no`, `snappy`, `zlib`, and `bzip2`, and expands to include `zstd`, `lz4`, `lz4hc`, and maybe `mixed`.
- Per-file deterministic deletion decisions use `md5sum`, `wc -l`, `sed`, and shell arithmetic.

## Control Flow
The script validates argument count, removes the target DB directory, probes `ldb` feature support, builds the compression list, enables `set -e`, seeds `n` from `$RANDOM`, and loops over every file from `ls -1 $input_data_dir`. For each file it chooses compression and dictionary byte settings from `n`, loads the file with `ldb load --auto_compaction=false --create_if_missing`, then uses the file hash to decide whether to delete a small key range. If `deleterange` is supported it creates a range tombstone from `key` to `key0`; otherwise it deletes the chosen key. It increments `n` after every file.

## State and Persistence Behavior
The script deletes the target DB at startup and creates a new one through `ldb`. Loaded data may remain in WALs until a later recovery because auto compaction is disabled. That behavior is intentional so generated DBs cover WAL format compatibility in addition to SST/table compatibility. Range tombstones or point deletes alter the logical contents deterministically based on input file hashes.

## Dependencies and Integration Points
Dependencies are Bash, `ldb`, `md5sum`, `grep`, `wc`, `sed`, and standard Unix tools. It integrates with `ldb load`, `ldb deleterange`, and `ldb delete`, and probes feature support for newer compression options.

## Risks and Edge Cases
- The script uses unquoted paths in several commands, so spaces or glob characters in input or DB paths can fail.
- Iterating `for f in \`ls -1\`` is not safe for filenames containing whitespace.
- `rm -rf $db_dir` is destructive and unquoted.
- `$RANDOM` makes compression assignment non-reproducible unless the shell seed is controlled, while deletion choice is deterministic per file.
- Dictionary compression support is inferred crudely from `ldb --version`.

## Test Signals
There is no formal test. Observable signals are echoed load/delete messages and successful completion under `set -e`. Any failing `ldb`, checksum, or file command aborts the script.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/generate_random_db.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/gtest_parallel_repro.py -->
# sources/storage-engines/rocksdb/tools/gtest_parallel_repro.py

## Purpose
`gtest_parallel_repro.py` repeatedly runs many fresh instances of a GoogleTest binary in parallel to reproduce flakes caused by process-level scheduling pressure, CPU starvation, or timing assumptions that do not appear in single-process `--gtest_repeat` loops.

## Important APIs, Types, and Functions
- Regexes `FAILURE_LINE_RE`, `SANITIZER_RE`, and `ASSERT_RE` extract failure keys from logs.
- Argument helpers include `positive_int()`, `parse_env()`, `resolve_cpu_list()`, and grouped parser builders for gtest, run control, output, CPU, and build flags.
- `build_if_requested()` optionally runs `make clean` and `make`, adding `COERCE_CONTEXT_SWITCH=1` when requested.
- `make_run_command()` builds the binary invocation and wraps it in `taskset -c` when CPU pinning is requested.
- Process lifecycle helpers include `launch_process()`, `launch_iteration_processes()`, `monitor_processes()`, `terminate_process()`, `terminate_processes()`, and `close_log_handles()`.
- Result helpers include `extract_failure_keys()`, `collect_process_result()`, `collect_iteration_results()`, `write_jsonl()`, `merge_histogram()`, and `print_summary()`.
- `prepare_run()` validates args, builds if needed, resolves CPU command, creates output directory, and writes `metadata.json`.
- `run_iterations()` runs the requested number of iterations, handles KeyboardInterrupt, supports `--stop-on-failure`, and returns failures plus histograms.

## Control Flow
`main()` parses arguments, prepares the run, prints command/output metadata, executes `iteration_count` batches of `processes_per_iteration` concurrent processes, writes `failures.jsonl`, prints totals and the top failure histogram, and returns one if failures occurred, zero if none occurred, or 130 if interrupted.

Each process gets its own run directory with `tmp/` assigned as `TEST_TMPDIR` and a combined stdout/stderr `log.txt`. After monitoring, successful run directories are deleted unless `--keep-success-artifacts` is set; failed or timed-out directories are retained and summarized.

## State and Persistence Behavior
Run state is written under `--out` or `/tmp/gtest_parallel_repro_<time>`. Persistent files include `metadata.json`, `failures.jsonl`, retained failure run directories, logs, and per-process `TEST_TMPDIR` contents. Successful artifacts are normally removed to keep output size bounded.

## Dependencies and Integration Points
The script uses only Python stdlib plus external `make`, the requested gtest binary, and optional `taskset`. It integrates with GoogleTest flags, environment overrides, RocksDB's optional `COERCE_CONTEXT_SWITCH` build mode, Unix process groups, and CPU affinity.

## Risks and Edge Cases
- `--out` must be empty if it exists, preventing accidental mixing of runs.
- `taskset` is required for `--cpus` or `--cpu-count`; unavailable taskset becomes a parser error.
- Timeout termination uses process groups where possible; binaries that spawn outside the group can escape.
- Failure-key extraction is heuristic and may group unrelated non-gtest failures under `<non-gtest failure>`.
- `--coerce-context-switch` only affects builds performed by this script; it warns but cannot verify an existing binary was built with that flag.

## Test Signals
The tool's own signal is exit status and generated summary. `TOTAL_RUNS`, `TOTAL_FAILURES`, `FAILURES_FILE`, and `FAILURE_HISTOGRAM` summarize reproduction quality. Retained logs and JSONL records provide per-process return code, elapsed time, log path, and failure keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/gtest_parallel_repro.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ingest_external_sst.sh -->
# sources/storage-engines/rocksdb/tools/ingest_external_sst.sh

## Purpose
This small Bash helper ingests every external SST file matching `extern_sst*` from a directory into a RocksDB database using `ldb ingest_extern_sst`.

## Important APIs, Types, and Functions
- Positional arguments are `<DB Path> <External SST Dir>`.
- The file discovery command is ``find $external_sst_dir -name extern_sst*``.
- Each file is ingested through `./ldb --db=$db_dir --create_if_missing ingest_extern_sst $f`.

## Control Flow
The script validates that at least two arguments are present, assigns `db_dir` and `external_sst_dir`, loops over matching files produced by `find`, prints a status line for each, and runs the `ldb` ingestion command. There is no explicit `set -e`, so failures do not necessarily stop later iterations.

## State and Persistence Behavior
The destination DB is created if missing and modified by each external SST ingestion. The script does not delete or move source SST files, does not compact after ingestion, and does not clean up a partially ingested DB on failure.

## Dependencies and Integration Points
Dependencies are Bash, `find`, and a `./ldb` binary in the current working directory. It integrates with RocksDB's external SST ingestion command exposed by `ldb`.

## Risks and Edge Cases
- Paths are unquoted, so whitespace in DB or SST paths breaks the command.
- The glob-like `extern_sst*` pattern is passed unquoted to `find`; shell expansion in the current directory can alter behavior.
- No `set -e` or return-code accumulation means the script may exit zero even if an ingestion fails before a later successful command.
- It assumes `./ldb`, not a configurable path.

## Test Signals
There is no formal test. Runtime signals are printed "Ingesting" lines and `ldb` exit messages. Callers should inspect command exit codes if robust automation is needed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ingest_external_sst.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser.cc -->
# sources/storage-engines/rocksdb/tools/io_tracer_parser.cc

## Purpose
This file is the minimal `main()` wrapper for the IO trace parser tool. It either delegates to `ROCKSDB_NAMESPACE::io_tracer_parser()` when gflags is available or reports that gflags is required.

## Important APIs, Types, and Functions
- gflags-disabled `main()` prints an error and returns one.
- gflags-enabled `main(int argc, char** argv)` includes `tools/io_tracer_parser_tool.h` and returns `io_tracer_parser(argc, argv)`.

## Control Flow
Compilation is split by `#ifndef GFLAGS`. In supported builds, all command parsing and record processing is handled by `io_tracer_parser_tool.cc`; this wrapper only forwards arguments and returns its status.

## State and Persistence Behavior
The wrapper owns no persistent state. State behavior is entirely in the parser implementation and the trace file it reads.

## Dependencies and Integration Points
The file integrates the reusable parser function with a standalone executable target. Its only implementation dependency under gflags is `tools/io_tracer_parser_tool.h`.

## Risks and Edge Cases
The only notable risk is build configuration: without gflags the tool cannot function and exits with an error. Runtime validation of `--io_trace_file` is delegated.

## Test Signals
The wrapper participates in `io_tracer_parser_test.cc` indirectly through the same parser function. Manual signal is the executable's exit code.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_test.cc -->
# sources/storage-engines/rocksdb/tools/io_tracer_parser_test.cc

## Purpose
This GoogleTest suite validates the IO trace parser by generating actual RocksDB IO trace files, invoking `io_tracer_parser()` in-process, and checking start/end tracing boundaries.

## Important APIs, Types, and Functions
- `IOTracerParserTest` fixture creates a per-thread test directory, trace file path, DB path, and a RocksDB DB with `create_if_missing=true`.
- `GenerateIOTrace()` creates a `TraceWriter`, calls `DB::StartIOTrace()`, performs ten Put+Flush operations, ends tracing with `DB::EndIOTrace()`, and verifies the trace file exists.
- `RunIOTracerParserTool()` builds an argv buffer containing `./io_tracer_parser` and `-io_trace_file=<path>`, then asserts `io_tracer_parser(argc, argv) == 0`.
- Tests are `InvalidArguments`, `DumpAndParseIOTraceRecords`, `NoRecordingAfterEndIOTrace`, and `NoRecordingBeforeStartIOTrace`.

## Control Flow
The fixture opens the DB at construction and destroys it plus the trace file and test directory in the destructor. `InvalidArguments` calls the parser without the required flag and expects failure. The dump/parse test generates a trace and parses it. The end-boundary test records trace file size after `EndIOTrace()`, performs more writes and flushes, and asserts the trace file size is unchanged. The before-start test writes and flushes before starting tracing and asserts no trace file exists, then generates and parses a trace.

## State and Persistence Behavior
The tests create real RocksDB data and real binary IO trace files under a per-thread temp directory. Trace file size is used as a persistence signal for whether operations after `EndIOTrace()` were recorded. DB teardown calls `DestroyDB()` with the fixture Env and deletes the test path.

## Dependencies and Integration Points
The suite depends on gflags, GoogleTest, RocksDB DB APIs, trace reader/writer APIs, `test_util`, and `tools/io_tracer_parser_tool.h`. Without gflags it builds a `main()` that reports the missing dependency and returns zero, effectively skipping the suite.

## Risks and Edge Cases
- Tests assert parser success but do not validate exact human-readable stdout.
- Trace generation relies on Put+Flush producing IO records on the current Env.
- The argv-building helper uses fixed-size buffers and repeats code from the invalid-argument test.
- File-size equality after `EndIOTrace()` is a coarse but useful boundary check.

## Test Signals
Passing tests confirm required argument validation, successful parsing of a generated trace, no recording before `StartIOTrace()`, and no recording after `EndIOTrace()`. The gtest `main()` installs the RocksDB stack trace handler.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.cc -->
# sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.cc

## Purpose
This file implements the IO trace parser tool. It reads a binary RocksDB IO trace file through the trace-reader abstraction and prints a human-readable header and one line per IO operation to stdout.

## Important APIs, Types, and Functions
- gflag `--io_trace_file` selects the binary input file.
- `IOTraceRecordParser::IOTraceRecordParser()` stores the input path.
- `PrintHumanReadableHeader()` prints start time and RocksDB major/minor versions from `IOTraceHeader`.
- `PrintHumanReadableIOTraceRecord()` prints access timestamp, file name, file operation, latency, IO status, optional file size/length/offset fields, and optional request ID.
- `ReadIOTraceRecords()` opens a `TraceReader` with `NewFileTraceReader()`, wraps it in `IOTraceReader`, reads the header, then reads records until `ReadIOOp()` returns a non-OK status.
- `io_tracer_parser()` parses flags, validates `FLAGS_io_trace_file`, constructs the parser, and returns its read status.

## Control Flow
The entry function parses command-line flags and rejects an empty trace path. The parser opens the trace file via `Env::Default()`, reads and prints the header, then loops while status is OK. For each successfully read `IOTraceRecord`, it formats required fields and decodes bitsets in `io_op_data` and `trace_data` by repeatedly finding the rightmost set bit.

## State and Persistence Behavior
The parser is read-only. It consumes an existing binary trace file and writes human-readable output to stdout. It does not create an output file despite the header comment mentioning `output_file_`.

## Dependencies and Integration Points
The implementation depends on gflags, RocksDB trace reader/writer APIs, `trace_replay/io_tracer.h`, `Env`, and `util/gflags_compat.h`. It integrates with traces generated by `DB::StartIOTrace()` and consumed by `IOTraceReader`.

## Risks and Edge Cases
- The implementation is compiled only under `GFLAGS`; otherwise no functions are defined from this file.
- Unknown bits in `io_op_data` or `trace_data` hit `assert(false)`, so newer trace formats can abort older parser builds.
- End-of-file is treated as a normal non-OK break and returns zero; corrupted trailing records might not be distinguished unless the reader reports an earlier open/header error.
- `log2(io_op_data & -io_op_data)` uses floating-point math for bit positions, which works for small enum bits but is less direct than integer bit operations.
- Output goes to stdout and cannot be redirected through a tool-specific flag.

## Test Signals
`io_tracer_parser_test.cc` checks empty-argument failure and successful parsing of generated traces. Runtime failures are returned as status one for missing/open/header errors; record-loop termination returns zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.h -->
# sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.h

## Purpose
This header declares the reusable IO trace parser API used by both the standalone parser binary and tests. It exposes `IOTraceRecordParser` and the `io_tracer_parser()` entry function.

## Important APIs, Types, and Functions
- Forward declarations: `IOTraceHeader` and `IOTraceRecord`.
- `class IOTraceRecordParser` stores an input file path and exposes `ReadIOTraceRecords()`.
- Private formatting helpers are `PrintHumanReadableHeader()` and `PrintHumanReadableIOTraceRecord()`.
- `int io_tracer_parser(int argc, char** argv)` is the CLI-compatible parser entry point.

## Control Flow
The header only declares control flow. The expected flow is construction with a binary input file, `ReadIOTraceRecords()` opening and walking records, and private print helpers formatting the header and records.

## State and Persistence Behavior
The only class state is `input_file_`, the path of the binary trace file. The parser does not own persistent output state at the type level.

## Dependencies and Integration Points
The header includes `rocksdb/env.h` and `rocksdb/status.h`, though the public declarations mostly need standard string support through included RocksDB headers. It is included by `io_tracer_parser.cc`, `io_tracer_parser_tool.cc`, and `io_tracer_parser_test.cc`.

## Risks and Edge Cases
- The private helper comments mention dumping records in `output_file_`, but the class has no output-file member; implementation prints to stdout. This stale comment can mislead users.
- Including heavier RocksDB headers in a small interface increases compile coupling.
- Because the CLI function is declared unconditionally but implemented only under gflags in the `.cc`, build targets must align compile definitions.

## Test Signals
The header has no standalone tests. Its declarations are exercised by the parser binary wrapper and the IO tracer parser gtest.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/io_tracer_parser_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb.cc -->
# sources/storage-engines/rocksdb/tools/ldb.cc

## Purpose
`ldb.cc` is the standalone entry point for RocksDB's `ldb` command-line tool. It constructs an `LDBTool` and delegates all command parsing and execution to `RunAndReturn()`.

## Important APIs, Types, and Functions
- Includes `rocksdb/ldb_tool.h`.
- `main(int argc, char** argv)` creates `ROCKSDB_NAMESPACE::LDBTool tool` and returns `tool.RunAndReturn(argc, argv)`.

## Control Flow
All runtime behavior is delegated to the library tool implementation. This wrapper has no local flag parsing, validation, or command dispatch.

## State and Persistence Behavior
State and persistence depend entirely on the selected `ldb` subcommand, such as load, get, put, delete, scan, dump, or ingestion commands. The wrapper itself owns no state.

## Dependencies and Integration Points
The file integrates the `LDBTool` library class into an executable. Scripts in this subset (`generate_random_db.sh` and `ingest_external_sst.sh`) depend on this executable for loading data, deleting ranges or keys, and ingesting external SSTs.

## Risks and Edge Cases
The wrapper is intentionally thin; any risks live in `LDBTool` or callers. Build/link failures are the main local risk because the entry point requires the ldb tool library.

## Test Signals
There are no local tests. Operational signal is the exit code returned from `LDBTool::RunAndReturn()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb.cc -->
