# Research: subset-b-008699

Grouped research for RocksDB tool sources. Each section preserves the source path and is intended to be split into the mapped source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb_cmd_test.cc -->
# sources/storage-engines/rocksdb/tools/ldb_cmd_test.cc

## Purpose
This GoogleTest suite validates the C++ `LDBCommandRunner`/`LDBCommand` path behind the `ldb` command-line tool. It covers help/version handling, hex conversion, mem-env operation, checksum reporting, blob-file checksum reporting, command-line option parsing, range-deletion listing, consistency-check toggles, column-family option loading, unsafe SST removal, manifest temperature updates, renamed DB option loading, and custom comparator operation.

## Important APIs, Types, and Functions
The file defines `LdbCmdTest`, whose `TryLoadCustomOrDefaultEnv()` loads a custom env from system configuration when available. `FileChecksumTestHelper` recalculates live-file checksums by opening each file through `Env::NewSequentialFile`, comparing generated checksums with `LiveFileMetaData`, and recovering a `VersionSet` to compare live metadata against MANIFEST checksum entries. `WrappedEnv` tests env-name preservation during options loading, and `MyComparator` verifies externally supplied comparator descriptors. Tests call `LDBCommandRunner::RunCommand`, `DB::Open`, `LoadLatestOptions`, `VersionSet::Recover`, `FileChecksumList::SearchOneFileChecksum`, and `SyncPoint` callbacks.

## Control Flow
Most tests create a temporary DB, write deterministic key ranges, flush to SST files, close the DB, invoke an `ldb` command through `RunCommand`, then reopen and assert data or metadata state. Checksum tests write overlapping key ranges across several flushes, run `file_checksum_dump`, recompute each file's checksum, compact a range, and repeat verification. `UnsafeRemoveSstFile` builds multiple SSTs, removes selected file numbers through `ldb unsafe_remove_sst_file`, and verifies reads across default and non-default column families. `FileTemperatureUpdateManifest` simulates observed file temperatures and verifies that `update_manifest --update_temperatures` persists them into the manifest.

## State and Persistence
The suite exercises persisted SST files, blob files, OPTIONS files, MANIFEST checksum records, column-family descriptors, and file temperature metadata. It intentionally closes DB instances before commands that require offline mutation. The checksum helper disables file deletions while inspecting live files, and `VerifyChecksumInManifest` reconstructs version metadata directly from MANIFEST state.

## Dependencies and Integration Points
It integrates with RocksDB internals (`VersionSet`, `VersionEdit`, `DBImpl`-level metadata), env wrappers, file checksum factories, blob-file support, options utilities, and the ldb command implementation in `tools/ldb_cmd_impl.h`. `RegisterCustomObjects` in `main()` keeps custom object loading available for env/config tests.

## Risks
These tests rely on exact internal metadata behavior, temporary DB cleanup, and `SyncPoint` names that can drift during refactors. Some checks use `char*` argv arrays and fixed buffers. Offline manifest/file mutation commands are inherently destructive if pointed at the wrong DB, so the command paths require strong validation. Checksum verification assumes live-file metadata and MANIFEST recovery enumerate comparable file sets.

## Test Signals
The file itself is a high-signal unit/integration suite. Passing tests indicate that ldb command dispatch, metadata mutation, checksum persistence, blob-file metadata, option loading, custom comparators, and file-temperature manifest updates remain compatible with RocksDB storage state.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb_cmd_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb_test.py -->
# sources/storage-engines/rocksdb/tools/ldb_test.py

## Purpose
This Python unittest module exercises the built `./ldb` executable as an end-user CLI. It validates simple put/get/delete flows, batch and entity writes, blob DB flags, scans, dump/load, hex and TTL modes, transaction DB opening, administrative commands, live-file dumps, manifest/WAL/SST/blob dumps, properties, column families, and external SST ingestion.

## Important APIs, Types, and Functions
`my_check_output()` is a compatibility wrapper around `subprocess.Popen` that raises on nonzero exit. `run_err_null()` shells a command while suppressing stderr. `LDBTestCase` owns a per-test temporary directory, `dbParam()`, `assertRunOKFull()`, `assertRunFAILFull()`, convenience wrappers for default DB calls, and helpers such as `dumpDb`, `loadDb`, `writeExternSst`, `ingestExternSst`, `dumpLiveFiles`, `listLiveFilesMetadata`, and file globbers for MANIFEST/SST/WAL/blob files.

## Control Flow
Each test creates an isolated temp directory in `setUp()` and removes it in `tearDown()`. Assertions run shell commands against `./ldb`, often filtering background-thread creation messages. Tests build data with `put`, `batchput`, `put_entity`, or blob-enabled writes, then validate command output exactly or with regexes. Dump/load tests pipe dump files into `ldb load`; metadata tests compare parsed output from two commands; corruption tests overwrite or remove SST files and expect `checkconsistency` failure.

## State and Persistence
The suite creates real DB directories and verifies persistence across separate `ldb` processes. It covers WAL files, MANIFEST files, SST files, blob files, OPTIONS loading, external SST files, and backup-like dump/load artifacts. TTL tests depend on timestamp-suffixed values; transaction tests create data through TransactionDB modes and verify normal reads where supported.

## Dependencies and Integration Points
It depends on a built `./ldb` binary in the current working directory, shell utilities (`cat`, `grep`, `ls`, `cp`, `rm`), Python `unittest`, and RocksDB command output formats. It is a broad integration layer over the C++ ldb command implementation.

## Risks
The tests are output-format sensitive and use shell=True command strings, so quoting and platform differences can cause fragility. A duplicate `testInvalidCmdLines` name means the later definition overrides the earlier one. Corruption tests use globbed SST output and destructive file writes/removes within the temp DB. Regex parsing of metadata commands can break on harmless formatting changes.

## Test Signals
Passing this suite is strong evidence that the installed `ldb` binary behaves correctly for common CLI workflows, file-format dump paths, column-family management, blob support, transaction flags, and external SST ingestion.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb_tool.cc -->
# sources/storage-engines/rocksdb/tools/ldb_tool.cc

## Purpose
This file implements the public `LDBTool` and `LDBCommandRunner` glue for the `ldb` command-line tool. It prints help text, handles top-level `--help`/`--version`, constructs the selected command object, validates command options, executes the command, reports execution state, and maps success/failure to process-style return codes.

## Important APIs, Types, and Functions
`LDBOptions::LDBOptions()` is defaulted. `LDBCommandRunner::PrintHelp()` builds a long help string from `LDBCommand` option constants and individual command `Help()` methods. `RunCommand()` calls `LDBCommand::InitFromCmdLineArgs`, `ValidateCmdLineOptions()`, `Run()`, and `GetExecuteState()`. `LDBTool::Run()` exits with `RunAndReturn()`, while `RunAndReturn()` returns the integer status to embedders/tests.

## Control Flow
`RunCommand()` first handles too few arguments, `--version`, and `--help` without constructing a command. For real commands, it creates a heap-allocated `LDBCommand`, rejects unknown or invalid commands, runs the command, prints any non-empty execution-state string to stderr, deletes the command, and returns `1` on failed state or `0` otherwise.

## State and Persistence
This file does not directly persist data. It passes `Options`, `LDBOptions`, and optional column-family descriptors into command construction. Persistence behavior belongs to the selected command classes in the ldb command implementation.

## Dependencies and Integration Points
It integrates `rocksdb/ldb_tool.h`, `rocksdb/utilities/ldb_cmd.h`, and `tools/ldb_cmd_impl.h`. The help surface enumerates data-access, admin, backup/restore, external-SST, unsafe-removal, and remote-compaction command classes, making it the central registry for user-visible ldb help.

## Risks
Help text can drift when new command flags are added but not documented here. `RunCommand()` owns a raw pointer and relies on all command paths returning normally after `Run()`. Any command that prints sensitive execution-state details will be emitted to stderr. The top-level argument threshold means commands with unusual one-argument forms must be handled before command creation.

## Test Signals
`ldb_cmd_test.cc` validates help/version and command execution return codes, while `ldb_test.py` validates the process-level CLI behavior that flows through this dispatcher.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/ldb_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/pflag -->
# sources/storage-engines/rocksdb/tools/pflag

## Purpose
`pflag` is a Bash process monitor. It periodically samples one resource metric for a target PID and takes an action when the measured value breaches a threshold. Supported metrics are virtual memory, RSS, and CPU time on Linux.

## Important APIs, Types, and Functions
The script defines `oscheck`, `verbose`, `warn`, `die`, `dump_config`, `usage`, `set_defaults_if_noopt_given`, and `validate_options`. Runtime variables include `PID`, `VAR`, `LIMIT`, `WAIT`, `N`, `ACTION`, and `DEBUG`. It uses `/bin/ps h -p "$PID" -o "$VAR"` and a Perl expression to normalize `m`/`g` suffixes.

## Control Flow
After parsing options with `getopts`, the script checks OS support, applies defaults (`VAR=vsz`, `LIMIT=1024000`, `WAIT=5`, high `N`, `ACTION=warn`), optionally dumps configuration, then loops until the process exits or the metric breaches the threshold. On breach it either warns and continues, kills the process, or exits after printing process details.

## State and Persistence
No persistent state is written. The only durable side effect can be process termination when `ACTION=kill`. Output goes to stdout/stderr.

## Dependencies and Integration Points
It depends on Bash, Linux `ps`, Perl, `kill`, `date`, and host process accounting. It is suitable for wrapping long-running benchmarks such as `db_bench`, although no direct caller is in this subset.

## Risks
The `-w` option is documented but the `getopts` string uses `t` instead of `w`, so wait parsing appears broken. `N` is logged but not decremented in the loop, so cycle limiting is ineffective. Numeric comparisons assume normalized integer values and can fail for unexpected `ps` output. `exit -1` maps to shell status 255. The script is Linux-only.

## Test Signals
No dedicated tests are present in this subset. Useful validation would include short-lived PID monitoring, threshold breach for each action, unit checks for `-w` parsing, and CPU-time threshold parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/pflag -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/reduce_levels_test.cc -->
# sources/storage-engines/rocksdb/tools/reduce_levels_test.cc

## Purpose
This GoogleTest suite validates the `ldb reduce_levels` command. It ensures that RocksDB databases can be reopened with fewer LSM levels after moving existing files down into the reduced level structure, without losing keys.

## Important APIs, Types, and Functions
`ReduceLevelTest` wraps a temporary DB path and a `std::unique_ptr<DB>`. It exposes `OpenDB`, `Put`, `Get`, `Flush`, `MoveL0FileToLevel`, `CloseDB`, `ReduceLevels`, and `FilesOnLevel`. Internally it uses `DBImpl::TEST_FlushMemTable`, `DBImpl::TEST_CompactRange`, `ReduceDBLevelsCommand::PrepareArgs`, and `LDBCommand::InitFromCmdLineArgs`.

## Control Flow
Tests create DBs with a fixed number of levels, write and flush keys, force compaction from L0 to target levels, close the DB, invoke the reduce-level command offline, reopen with the new level count, and assert file placement or key readability. `Last_Level` repeatedly collapses a DB with data at the bottom level. `Top_Level` validates reductions with only L0 data. `All_Levels` populates levels 1 through 4, then reduces to 4, 3, and 2 levels while verifying all keys.

## State and Persistence
The test manipulates real RocksDB files under a per-thread path. The reduce command persists updated metadata such that reopening with fewer `num_levels` succeeds. Data persistence is validated through `Get` after each reduction.

## Dependencies and Integration Points
It integrates DB internals, `tools/ldb_cmd_impl.h`, `util/cast_util.h`, and RocksDB test harness utilities. It directly selects the ldb command implementation rather than spawning a process.

## Risks
The test uses internal `TEST_` DBImpl methods and static casting, making it sensitive to compaction internals. It only tests default column family and basic value keys. It does not assert detailed manifest edits beyond reopen and file-count behavior.

## Test Signals
Passing tests signal that level-reduction command arguments, offline manifest edits, and DB recovery with reduced level counts work for top-level, bottom-level, and multi-level file layouts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/reduce_levels_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/regression_test.sh -->
# sources/storage-engines/rocksdb/tools/regression_test.sh

## Purpose
This Bash script automates RocksDB performance regression testing. It builds `db_bench` and `ldb`, prepares local or remote benchmark directories, optionally builds a base DB, checkpoints it, runs a fixed benchmark sequence, parses throughput/latency/time output, and writes a CSV summary.

## Important APIs, Types, and Functions
Core functions are `main`, `init_arguments`, `run_db_bench`, `set_async_io_parameters`, `build_checkpoint`, `update_report`, `exit_on_error`, `build_db_bench_and_ldb`, `run_remote`, `test_remote`, `setup_options_file`, `setup_test_directory`, and `cleanup_test_directory`. It uses many environment variables for paths, benchmark sizes, thread counts, compaction settings, cache sizes, async I/O tuning, remote shell/copy commands, and cleanup policy.

## Control Flow
`main` initializes defaults, arms an EXIT trap, builds binaries, prepares directories, optionally runs `fillseq,compactall`, moves the built DB to an origin path, then checkpoints and runs read/write/delete/seek/multiread benchmarks. `run_db_bench` kills stale `db_bench` processes, refuses to run when recent ones exist, builds a long `db_bench` command, optionally wraps it in SSH, tees output to a result file, and calls `update_report`.

## State and Persistence
The script creates and deletes benchmark DB, WAL, binary, result, and checkpoint directories. It writes `SUMMARY.csv` and one log per benchmark. It may leave DB/WAL state for debugging unless `DELETE_TEST_PATH` is nonzero. Remote mode copies binaries and options to the target host.

## Dependencies and Integration Points
It depends on `make`, `db_bench`, `ldb checkpoint`, `time`, `bc`, `grep`, `awk`, `tail`, `pidof`, `stat`, SSH/SCP, and either Mercurial or Git for commit IDs. It integrates benchmark output formats with CSV parsing regexes.

## Risks
The script uses `eval` extensively with environment-derived command strings and path variables. Cleanup uses `rm -rf` after basic non-dot checks, so path mistakes are dangerous. `build_checkpoint` assigns `dirs=$?` after `find`, which captures exit status rather than output and appears suspect for multi-DB mode. Output parsing is brittle to db_bench format changes. Remote command quoting is fragile.

## Test Signals
The primary signal is a completed `SUMMARY.csv` without `ERROR` lines and benchmark logs containing parseable throughput/percentiles. There are no unit tests in this subset for script behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/regression_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/restore_db.sh -->
# sources/storage-engines/rocksdb/tools/restore_db.sh

## Purpose
This tiny Bash wrapper restores the latest backup from a RocksDB backup directory into a DB directory by invoking `./ldb restore`.

## Important APIs, Types, and Functions
There are no functions. It validates that at least two arguments are present, assigns `backup_dir="$1"` and `db_dir="$2"`, logs the restore operation, and runs `./ldb restore --db="$db_dir" --backup_dir="$backup_dir"`.

## Control Flow
The script exits with usage status `1` when required arguments are missing. Otherwise it delegates all real work and exit behavior to `ldb restore`.

## State and Persistence
The target DB path can be created or overwritten according to `ldb restore` semantics. The script itself writes no metadata.

## Dependencies and Integration Points
It assumes `./ldb` exists in the current working directory and supports the `restore` command. It integrates with RocksDB backup/restore tooling through the ldb command surface.

## Risks
There is no validation that paths are safe, empty, local, or distinct. Additional restore options cannot be passed through. Running from the wrong directory fails or invokes the wrong `ldb` binary.

## Test Signals
No dedicated tests are present here. A practical signal is successful restore followed by `ldb checkconsistency` or application-level reads from the restored DB.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/restore_db.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/rocksdb_dump_test.sh -->
# sources/storage-engines/rocksdb/tools/rocksdb_dump_test.sh

## Purpose
This shell smoke test verifies that a bundled sample dump can be imported with `rocksdb_undump`, exported with `rocksdb_dump --anonymous`, and compared byte-for-byte with the original dump.

## Important APIs, Types, and Functions
The script uses `mktemp -d` to create `TESTDIR`, sets `DUMPFILE=tools/sample-dump.dmp`, then invokes `./rocksdb_undump`, `./rocksdb_dump`, and `cmp`.

## Control Flow
It creates a temporary DB path, undumps the sample into `$TESTDIR/db`, dumps that DB back to `$TESTDIR/dump`, and compares the files. There is no explicit cleanup or shell `set -e`; failure depends on the final command status unless the caller runs with strict shell settings.

## State and Persistence
It writes a temporary DB and dump file under `${TMPDIR:-/tmp}`. The temp directory is not removed by the script, so repeated runs leave artifacts.

## Dependencies and Integration Points
It depends on built `rocksdb_undump` and `rocksdb_dump` binaries in the working directory and the sample dump at `tools/sample-dump.dmp`.

## Risks
Missing `set -e` means an early undump failure could be masked until `cmp`. There is no trap cleanup. The test is intentionally narrow and only covers anonymous round-tripping for one fixture.

## Test Signals
The key signal is `cmp` success, proving the sample dump can round-trip exactly through the dump/undump tools.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/rocksdb_dump_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/run_blob_bench.sh -->
# sources/storage-engines/rocksdb/tools/run_blob_bench.sh

## Purpose
This Bash script runs a predefined BlobDB benchmark sequence through `tools/benchmark.sh`. It covers write-only, read-write, and read-only phases with blob-file and blob-cache options exposed through environment variables.

## Important APIs, Types, and Functions
`display_usage` documents required paths and tunables. The script validates `DB_DIR`, `WAL_DIR`, `OUTPUT_DIR`, and the presence of `tools/benchmark.sh`. It computes size defaults, blob options, target SST file size, and level-base size, then builds `ENV_VARS`, `ENV_VARS_D`, `PARAMS`, and `PARAMS_GC` strings passed to benchmark invocations.

## Control Flow
After argument and environment validation, it prints the benchmark setup, removes old DB/WAL/output directories, and runs six benchmark phases: `bulkload`, `overwrite`, `readwhilewriting`, `fwdrangewhilewriting`, `readrandom`, and `fwdrange`. It copies RocksDB `LOG*` files into the output directory at the end.

## State and Persistence
It destructively recreates the DB, WAL, and output directories. Benchmark results and copied logs persist in `OUTPUT_DIR`. No checkpointing or resume behavior is implemented.

## Dependencies and Integration Points
It depends on Bash, `env -S`, `rm`, `cp`, and `tools/benchmark.sh`, which in turn drives `db_bench`. It integrates with BlobDB options such as blob file size, blob GC thresholds, blob cache settings, and starting level.

## Risks
`rm -rf` is run on environment-provided directories after only non-empty validation. `env -S` is not portable to all Unix environments. Option strings are assembled as shell words and can break with spaces. The derived `target_file_size_base` formula changes dramatically when blob files are enabled and should be understood before comparing runs.

## Test Signals
Successful completion leaves benchmark logs and a `report.tsv`/benchmark output from `benchmark.sh`, plus RocksDB LOG files copied into `OUTPUT_DIR`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/run_blob_bench.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/run_clang_tidy.py -->
# sources/storage-engines/rocksdb/tools/run_clang_tidy.py

## Purpose
This Python tool runs `clang-tidy` on changed C/C++ source files and filters diagnostics to lines changed by local commits, staged/unstaged edits, and untracked files. It supports CI annotations, GitHub step summaries, PR comment bodies, parallel execution, explicit diff bases, and optional full-output capture.

## Important APIs, Types, and Functions
Key functions include `run_cmd`, `get_repo_root`, `find_remote_base`, `resolve_diff_base`, `parse_diff_for_changed_lines`, `collect_changed_lines`, `load_compile_db`, `invoke_clang_tidy`, `filter_to_changed_lines`, `emit_github_annotations`, `build_markdown_summary`, `write_github_step_summary`, `write_comment_file`, and `main`. It uses `ThreadPoolExecutor` to run clang-tidy jobs concurrently.

## Control Flow
`main` parses CLI options, discovers the repo root and compile database, resolves the diff base, collects changed line numbers, filters to changed `.cc`/`.cpp` files present in `compile_commands.json`, runs clang-tidy for each file, filters diagnostics to changed lines, optionally writes raw output, emits summaries/annotations/comments, and exits nonzero only when errors are found.

## State and Persistence
The script reads Git state and `compile_commands.json`. It can write a full raw output file, append to `$GITHUB_STEP_SUMMARY`, and write a Markdown comment body containing a stable HTML marker. It does not modify source files.

## Dependencies and Integration Points
It depends on Git, Python 3, clang-tidy, a CMake-style `compile_commands.json`, and GitHub Actions environment conventions when CI flags are used. It integrates with PR workflows by limiting reported findings to changed lines.

## Risks
Diff parsing is custom and may miss rename/delete edge cases or unusual diff headers. Explicit `--diff-base` intentionally ignores working-tree changes. Untracked headers are counted, but only `.cc`/`.cpp` files are linted. The script exits `0` for warnings-only findings, which may or may not match policy. Markdown includes GitHub emoji shortcodes and details blocks, so consumers should support GitHub-flavored Markdown.

## Test Signals
Useful validation includes no-change runs, untracked-file runs, explicit-base CI runs, timeout handling, annotation formatting, and compile database filtering. No dedicated unit tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/run_clang_tidy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/run_flash_bench.sh -->
# sources/storage-engines/rocksdb/tools/run_flash_bench.sh

## Purpose
This Bash script runs a broad flash-storage benchmark sequence with RocksDB `tools/benchmark.sh`. It prepares or restores a database, runs setup writes, read-only tests, read-write tests, merge tests, and a universal compaction test, then builds summarized reports.

## Important APIs, Types, and Functions
The script is top-level imperative Bash. It defines size constants and tunables from environment variables such as `NKEYS`, write rate limits, duration, range length, value size, block/cache sizes, data/WAL dirs, setup/save flags, and `SKIP_LOW_PRI_TESTS`. It builds an `ARGS` environment string and repeatedly invokes `./tools/benchmark.sh`.

## Control Flow
It chooses requested thread counts from command-line arguments or defaults to 24. In setup mode it may run `bulkload`, large and normal `fillseq` with WAL disabled/enabled, and single-threaded overwrite. Restore mode copies `.bak` directories back into place. It optionally saves setup backups, then loops over thread counts for readrandom/range scans, overwrite/update/readwhilewriting/rangewhilewriting, merge workloads, and universal compaction. Finally it greps `report.txt` into `report2.txt`.

## State and Persistence
The script writes benchmark output under `${TMPDIR:-/tmp}/output`, creates/modifies `DATA_DIR` and `LOG_DIR`, and can copy persistent `.bak` snapshots. It deletes and restores directories with `rm -rf` and `cp -p -r`.

## Dependencies and Integration Points
It depends on `tools/benchmark.sh`, shell utilities, and RocksDB `db_bench` behavior through benchmark wrappers. Report construction assumes the format emitted by `benchmark.sh`.

## Risks
Environment-provided paths are removed without robust safety guards. Some summary lines duplicate redirects, for example `echo readwhile >> $output_dir/report2.txt >> $output_dir/report2.txt`. Grep patterns are brittle and can fail if test names change. Long default durations and key counts can be expensive. No `set -e` means intermediate failures may not stop the script unless `benchmark.sh` handles them.

## Test Signals
Successful runs produce `report.txt`, `report2.txt`, and per-test output logs. Comparing report rows across runs is the primary regression signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/run_flash_bench.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/run_leveldb.sh -->
# sources/storage-engines/rocksdb/tools/run_leveldb.sh

## Purpose
This Bash script runs a LevelDB-compatible benchmark sequence using `tools/benchmark_leveldb.sh`. It is intended for comparing RocksDB and a specific LevelDB fork, with setup writes followed by read-only and read-write workloads.

## Important APIs, Types, and Functions
The script is top-level Bash and uses environment tunables `NKEYS`, `NWRITESPERSEC`, `VAL_SIZE`, `BLOCK_LENGTH`, `CACHE_BYTES`, `DATA_DIR`, `DO_SETUP`, and `SAVE_SETUP`. It builds `ARGS` and calls `./tools/benchmark_leveldb.sh` for `fillseq`, `overwrite`, `readrandom`, and `readwhilewriting`.

## Control Flow
It parses optional thread-count arguments or defaults to 24. Setup mode creates the DB through large-value fillseq, normal fillseq, and single-threaded overwrite. Restore mode copies `${DATA_DIR}.bak` into place. Optional save mode refreshes the backup. It then loops over thread counts for random reads and overwrite/readwhilewriting tests, and builds `report2.txt` from `report.txt` with grep filters.

## State and Persistence
It writes output to `${TMPDIR:-/tmp}/output`, creates/removes `DATA_DIR`, and can create or restore `${DATA_DIR}.bak`. There is no WAL-dir handling because LevelDB benchmark settings differ from RocksDB.

## Dependencies and Integration Points
It depends on `tools/benchmark_leveldb.sh`, shell utilities, and the modified LevelDB benchmark interface described in the comments. It is operationally parallel to `run_flash_bench.sh` but for LevelDB.

## Risks
It lacks strict shell failure handling and uses `rm -rf` on environment-derived paths. Summary greps include tests that are commented out, so some sections may be empty. The header comment references `run_flash_bench.sh`, likely copied text. Defaults are large and can produce expensive runs.

## Test Signals
Successful completion produces `report.txt`, `report2.txt`, and per-test logs under the output directory. The reports are the comparison signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/run_leveldb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/simulated_hybrid_file_system.cc -->
# sources/storage-engines/rocksdb/tools/simulated_hybrid_file_system.cc

## Purpose
This file implements a development-only `FileSystemWrapper` that simulates hybrid storage by adding latency and IOPS throttling to warm files. It is designed for benchmark experiments that need slower warm-tier behavior while preserving warm-file membership across runs.

## Important APIs, Types, and Functions
`CalculateServeTimeUs()` models service time as fixed latency plus byte-dependent cost. `RateLimiterRequest()` adapts a byte-oriented `RateLimiter` to request-count-like timing. `SimulatedHybridFileSystem` loads/stores warm file metadata, wraps random-access and writable files, and removes deleted files from the warm set. `SimulatedHybridRaf` overrides `Read`, `MultiRead`, and `Prefetch`. `SimulatedWritableFile` overrides append, positioned append, and sync methods.

## Control Flow
Construction creates a generic rate limiter based on the throughput multiplier and loads newline-separated warm filenames from the metadata file when present. `NewRandomAccessFile` determines whether a file is warm based on full-FS mode or the warm set, creates the target file, then wraps it in `SimulatedHybridRaf`. `NewWritableFile` records warm files and wraps writes when appropriate. Reads and direct writes simulate wait immediately; buffered writes accumulate `unsynced_bytes` and simulate on `Sync`.

## State and Persistence
The warm-file set is protected by a mutex and persisted as a newline-separated metadata file in the destructor. `DeleteFile` removes entries from the set. Runtime state includes rate limiter tokens and unsynced byte counts.

## Dependencies and Integration Points
It depends on RocksDB `FileSystem`, `RateLimiter`, `StopWatchNano`, `Env::SleepForMicroseconds`, and file utility helpers. It integrates through `FileOptions::temperature` and RocksDB file creation/read paths.

## Risks
Constructor read failures call `std::exit(1)`, which is harsh for library code but intentional for benchmarks. `NewRandomAccessFile` wraps `result` even if target creation fails, which could be risky if callers expect `result` to be valid only on success. Warm metadata is unordered and rewritten only on destruction. The model is approximate and not production-safe.

## Test Signals
No direct tests are present in this subset. Benchmark runs using warm temperatures should show added latency/IOPS throttling and metadata persistence across process restarts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/simulated_hybrid_file_system.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/simulated_hybrid_file_system.h -->
# sources/storage-engines/rocksdb/tools/simulated_hybrid_file_system.h

## Purpose
This header declares the simulated hybrid file system used by benchmark/development tooling. It exposes wrappers for a `FileSystem`, random-access files, and writable files that can inject warm-storage latency and rate limiting.

## Important APIs, Types, and Functions
`SimulatedHybridFileSystem` derives from `FileSystemWrapper` and overrides `NewRandomAccessFile`, `NewWritableFile`, `DeleteFile`, and `Name`. It stores a `RateLimiter`, mutex, warm file set, metadata filename, display name, and full-FS-warm flag. `SimulatedHybridRaf` derives from `FSRandomAccessFileOwnerWrapper` and overrides `Read`, `MultiRead`, and `Prefetch`. `SimulatedWritableFile` derives from `FSWritableFileWrapper` and overrides append, positioned append, and `Sync`.

## Control Flow
The declarations establish a wrapping design: the file system decides whether a file is warm and returns wrappers; the file wrappers call private `SimulateIOWait()` before delegating to the target file. Writable files distinguish direct I/O, which waits per append, from buffered I/O, which accumulates bytes until sync.

## State and Persistence
The file system owns warm-file membership and a metadata filename for cross-run persistence. Random-access wrappers hold immutable temperature state. Writable wrappers hold the owned target file and an `unsynced_bytes` accumulator.

## Dependencies and Integration Points
It includes `rocksdb/file_system.h` and uses RocksDB `Temperature`, `RateLimiter`, `IOOptions`, `FileOptions`, and `IODebugContext` types. It is meant to be plugged into RocksDB options/env configuration for benchmark runs.

## Risks
The header notes this is development-only and should not be used in production. Thread-safety is limited to warm-set management; per-file accumulators are not externally synchronized. Consumers must understand that warm classification changes I/O latency and may persist between runs through metadata.

## Test Signals
Signals come from the implementation and benchmark behavior: wrapped warm reads/writes should be slower, deletion should remove warm metadata, and reopening with metadata should restore warm classification.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/simulated_hybrid_file_system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/sst_dump.cc -->
# sources/storage-engines/rocksdb/tools/sst_dump.cc

## Purpose
This is the executable entry point for the `sst_dump` tool. It constructs an `SSTDumpTool` and returns its `Run()` status.

## Important APIs, Types, and Functions
The only function is `main(int argc, char** argv)`, which includes `rocksdb/sst_dump_tool.h`, creates `ROCKSDB_NAMESPACE::SSTDumpTool tool`, and calls `tool.Run(argc, argv)`.

## Control Flow
All argument parsing, file traversal, and dumping logic is delegated to `SSTDumpTool::Run` in `sst_dump_tool.cc`.

## State and Persistence
This wrapper has no state of its own. Persistence side effects, such as raw dump output files, occur inside the tool implementation for selected commands.

## Dependencies and Integration Points
It links the standalone binary to the reusable `SSTDumpTool` class, allowing tests to call the same class directly without process spawning.

## Risks
There is minimal local risk. Any process initialization such as stack trace handlers or custom object registration must happen elsewhere if needed; this wrapper does not add it.

## Test Signals
`sst_dump_test.cc` tests `SSTDumpTool` directly. Process-level testing of this file is equivalent to invoking the compiled binary with help/version or SST inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/sst_dump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/sst_dump_test.cc -->
# sources/storage-engines/rocksdb/tools/sst_dump_test.cc

## Purpose
This GoogleTest suite validates `SSTDumpTool` and related `SstFileDumper` behavior. It creates synthetic SST files and verifies raw dumps, scans/checks, recompression, compression managers, memory environments, readahead sizing, file path validity, mmap reads, meta-block listing, and record-count verification.

## Important APIs, Types, and Functions
Helpers include `MakeKey`, `MakeKeyWithTimeStamp`, `MakeValue`, `MakeWideColumn`, and `cleanup`. `SSTDumpToolTest` manages a temp directory/env, owns `PopulateCommandArgs`, `createSST`, and `SSTDumpToolTestCase`. `MyManager` is a custom `CompressionManager` for dependency-injection testing. Tests use `TableBuilder`, `BlockBasedTableFactory`, `SstFileDumper`, `SyncPoint`, `SaveAndRestore`, and `ObjectLibrary`.

## Control Flow
Tests build SST files by writing internal keys to a `TableBuilder`, then invoke `SSTDumpTool::Run` with constructed argv arrays. Generic cases cover `raw`, `show_properties`, `recompress`, `verify`, and `list_meta_blocks`. Path tests run combinations of missing files, valid SSTs, directories, text files, fake SSTs, and `--` argument handling. Record verification tests intentionally corrupt table property counts through `SyncPoint` and verify corruption is reported only for full scans without range/read limits.

## State and Persistence
The suite writes temporary `.sst` and `_dump.txt` files under a per-thread test directory, cleaning them unless `KEEP_DB` is set. It can register a custom compression manager in the default object library, which is process-global test state.

## Dependencies and Integration Points
It integrates table building, block-based table options, wide-column serialization, custom comparators, timestamp comparators, compression infrastructure, env/mem-env support, file readers, and the public dump tool.

## Risks
The tests allocate argv buffers manually and rely on exact command aliases, output file naming, and sync-point names. The custom compression-manager test is conditional on codec support. Path-validity expectations distinguish single invalid file failure from mixed valid/invalid success, which should remain documented.

## Test Signals
Passing tests indicate that the dump tool can parse options, identify valid SSTs, dump/read/recompress tables, handle env variants, honor readahead, and detect entry-count mismatches.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/sst_dump_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/sst_dump_tool.cc -->
# sources/storage-engines/rocksdb/tools/sst_dump_tool.cc

## Purpose
This file implements `SSTDumpTool::Run`, the core logic for the `sst_dump` command. It parses CLI options, discovers SST files from files/directories, configures env/table/compression options, invokes `SstFileDumper`, and performs scan/check/raw/verify/recompress/identify/property/meta-block operations.

## Important APIs, Types, and Functions
`print_help()` emits usage and supported compression types. `ParseIntArg()` parses integer flags and exits on malformed numeric input. `SSTDumpTool::Run()` owns all command parsing and execution. It uses `Env::CreateFromUri`, `OptionsHelper::compression_type_string_map`, `CompressionManager::CreateFromString`, `LDBCommand::HexToString`, `ParseInternalKey`, `SstFileDumper::ReadSequential`, `DumpTable`, `VerifyChecksum`, `ShowAllCompressionSizes`, `ReadTableProperties`, and meta-index block iteration.

## Control Flow
`Run()` initializes defaults, registers custom compression managers, parses arguments, validates paired compression-level flags and prefix/from conflicts, decodes hex range keys, and requires at least one file or directory. It expands directories by listing children, filters to `.sst`, constructs an `SstFileDumper` for each valid SST, optionally filters by property regexes, then executes the selected command. It accumulates summary counters and valid SSTs. At the end it prints identify results when requested and returns failure if no valid SST files were found.

## State and Persistence
Most commands are read-only. `raw` writes `<sst_basename>_dump.txt`. `recompress` simulates table output sizes and mutates local `Options` table/compression settings before each file. Summary counters track file/block/size totals in memory.

## Dependencies and Integration Points
It depends on RocksDB env creation, table factories, block contents, compression managers, db_stress compression registration, and ldb hex parsing. It is called by `sst_dump.cc` and directly by `sst_dump_test.cc`.

## Risks
The parser is manual and mixes `exit(1)` with returned error codes, which can surprise embedders. Some boolean parsing accepts only first-character truthiness. Directory expansion scans direct children only. `--command=verify_checksum` appears accepted by tests through behavior equivalent to validation paths, although help lists `verify`. Mutating `options` inside the per-file loop can affect later files. Regex filters are intentionally niche and depend on property string formatting.

## Test Signals
`sst_dump_test.cc` covers help/version, raw dumps, recompression, custom compression manager, mem env, readahead, path validity, mmap reads, and record-count mismatch detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/sst_dump_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/tool_hooks.cc -->
# sources/storage-engines/rocksdb/tools/tool_hooks.cc

## Purpose
This file implements default tool hooks for opening RocksDB database variants. The hook layer centralizes DB creation/opening calls so tools can use a replaceable indirection point instead of hard-coding every open operation.

## Important APIs, Types, and Functions
`DefaultHooks` methods wrap `DB::Open`, `DB::OpenForReadOnly`, `TransactionDB::Open`, `OptimisticTransactionDB::Open`, `DB::OpenAsSecondary`, `DB::OpenAsFollower`, and `blob_db::BlobDB::Open`. The file defines the global `DefaultHooks defaultHooks`.

## Control Flow
Every method is a direct pass-through from tool hook arguments to the corresponding RocksDB API. Overloads cover single-CF and multi-CF DB opens, read-only opens, transaction DBs with options and column-family descriptors, optimistic transaction DBs, secondary/follower opens, and legacy BlobDB opens.

## State and Persistence
The file itself stores only the global hook object. Persistent effects are those of the underlying DB open calls, such as creating/opening DB directories, recovering WALs, or initializing handles according to options.

## Dependencies and Integration Points
It includes `rocksdb/tool_hooks.h`, DB/convenience/options headers, transaction DB utilities, optimistic transaction DB utilities, and BlobDB. Tools can depend on `defaultHooks` for normal behavior while tests or specialized builds can provide alternate hook implementations.

## Risks
As a thin wrapper, it can silently lag new open modes unless the hook interface is updated. Default arguments in the `.cc` definition for `OpenForReadOnly` should match the declaration to avoid confusion. The global hook object has process-wide lifetime.

## Test Signals
Indirect signals come from ldb and other tool tests that open DBs in normal, read-only, transaction, secondary/follower, or blob modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/tool_hooks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/trace_analyzer.cc -->
# sources/storage-engines/rocksdb/tools/trace_analyzer.cc

## Purpose
This is the executable entry point for RocksDB trace analysis. It either reports that gflags is required or delegates to the real trace analyzer tool when compiled with gflags support.

## Important APIs, Types, and Functions
Without `GFLAGS`, `main()` prints `Please install gflags to run rocksdb tools` to stderr and exits `1`. With `GFLAGS`, `main(int argc, char** argv)` includes `tools/trace_analyzer_tool.h` and returns `ROCKSDB_NAMESPACE::trace_analyzer_tool(argc, argv)`.

## Control Flow
Compile-time preprocessor selection decides which binary behavior is built. Runtime logic is otherwise a direct delegation.

## State and Persistence
This wrapper has no state. Trace input/output behavior belongs to `trace_analyzer_tool`.

## Dependencies and Integration Points
It integrates the trace analyzer executable with the optional gflags dependency. Build configuration controls whether the functional implementation is available.

## Risks
Users can build a binary that always fails if gflags is absent. The non-gflags path gives no remediation beyond installing gflags. No argument validation occurs in the wrapper.

## Test Signals
A useful smoke test is invoking the binary in both build configurations: non-gflags should return `1` with the dependency message, while gflags builds should expose the analyzer tool's CLI behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/trace_analyzer.cc -->
