<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_test.cc -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_test.cc

## Purpose
This is the unit/integration test driver for RocksDB's block cache trace analyzer. It synthesizes block cache trace files with controlled metadata, invokes both the analyzer CLI entry point and the `BlockCacheTraceAnalyzer` class directly, and validates the CSV artifacts and in-memory aggregates that the analyzer produces.

## Important APIs, Types, and Functions
The file is compiled only when `GFLAGS` is available; without gflags it provides a stub `main` that prints an installation message and returns success. In the real test build it uses RocksDB test infrastructure (`testing::Test`, `ASSERT_OK`, `EXPECT_OK`), environment APIs (`Env`, `EnvOptions`, `NewFileTraceWriter`, `NewFileTraceReader`), trace APIs (`BlockCacheTraceWriter`, `BlockCacheTraceReader`, `BlockCacheTraceRecord`, `BlockCacheTraceHeader`), analyzer APIs (`BlockCacheTraceAnalyzer`, `block_cache_trace_analyzer_tool`), and parsing helpers (`ParseDouble`, `ParseInt`, `ParseUint32`).

`BlockCacheTracerTest` owns all test paths and analyzer option strings. Its constructor creates a per-thread temp directory, chooses paths for the trace and cache simulator config, and sets comma-delimited labels/buckets for timeline, reuse distance, reuse interval, reuse lifetime, caller, access count, and GET spatial locality analysis. Its destructor removes the trace file and test directory unless `KEEP_DB` is set, in which case it prints the retained trace path.

`GetCaller` maps key ids modulo five to `kPrefetch`, `kCompaction`, `kUserGet`, `kUserMultiGet`, and `kUserIterator`, giving generated traces an even caller distribution. `WriteBlockAccess` emits a sequence of `BlockCacheTraceRecord` values with deterministic timestamps, sizes, block keys, column family, level, caller, SST file number, referenced key fields, and key counts. `AssertBlockAccessInfo` checks analyzer aggregate state for a generated block, including per-caller counts and data-block referenced-key stats for GET/MultiGet callers. `RunBlockCacheTraceAnalyzer` builds an argv buffer and calls `ROCKSDB_NAMESPACE::block_cache_trace_analyzer_tool` with the generated trace, simulator config, output directory, and many analysis flags.

The tests are `BlockCacheAnalyzer`, `MixedBlocks`, and `MultiGetWithNullReferenceKey`. The file-level `main` installs RocksDB's stack trace handler, initializes the test harness, and runs all tests.

## Control Flow
`BlockCacheAnalyzer` first writes 50 synthetic data-block accesses to a binary trace and writes a cache simulator config (`lru,1,0,1K,1M,1G`). It then invokes the analyzer CLI path with analysis flags enabled. After that it opens the generated outputs under the test directory and checks each artifact: miss ratio curve, miss ratio/miss timelines for configured capacities and trace-only mode, skewness, access timelines, reuse interval/distance/lifetime summaries, percentage-of-accesses summaries, per-caller breakdowns, access-count summaries, reuse-block timelines, and GET spatial locality files. Each artifact is deleted after validation, and the simulator config is removed at the end.

`MixedBlocks` writes five groups of ten block records covering uncompression dictionary, data, filter, index, and range deletion blocks. It reads and checks the trace header, runs `BlockCacheTraceAnalyzer::Analyze`, expects `Status::Incomplete("")` at trace end, then inspects `TEST_cf_aggregates_map()` to verify one column family, two SST file numbers, one level, five block types per file, and the expected split of odd/even block keys across SST numbers.

`MultiGetWithNullReferenceKey` writes the same mixed block-type trace but asks `WriteBlockAccess` to blank the referenced key for MultiGet callers and set `get_from_user_specified_snapshot`. It then runs the analyzer with a human-readable trace output path, expects normal incomplete-at-end status, and deletes the human-readable file. This covers trace records whose MultiGet referenced key is intentionally absent.

## State and Persistence Behavior
The test persists temporary files under `test::PerThreadDBPath("block_cache_trace_analyzer_test")`: the binary trace, cache simulator config, human-readable trace, and many analyzer CSV outputs. Generated records use deterministic timestamps of `(key_id + 1) * kMicrosInSecond`, deterministic block sizes of `1024 + key_id`, deterministic keys, and deterministic SST assignment by parity. State that matters to the assertions is either stored in trace files and CSV files or exposed from analyzer aggregate maps. Cleanup is explicit: most output files are removed inside assertions, while the fixture destructor removes the trace and directory unless `KEEP_DB` requests preservation for debugging.

## Dependencies and Integration Points
The test integrates the block cache tracer writer/reader with the analyzer and the analyzer CLI wrapper. It depends on the gflags-enabled tool entry point, RocksDB's file environment, system clock access, the RocksDB test harness, trace record encoding, cache simulator config parsing, and output naming conventions used by the analyzer. The test is also tightly coupled to the analyzer's CSV schemas, output file names, label expansion rules, and the test-only aggregate accessor `TEST_cf_aggregates_map()`.

## Risks and Edge Cases
The assertions depend on exact output file names, CSV column counts, percentage totals, cache name formatting, and parseable decimal output, so legitimate analyzer formatting changes can break the test even when semantics are preserved. The argv construction in `RunBlockCacheTraceAnalyzer` is bounded by `kMaxArgCount` and `kArgBufferSize`; adding many flags or long labels requires updating those limits. The fixture destructor assumes the trace file and directory exist unless `KEEP_DB` is set, which can create noisy failures if setup fails before creation. The analyzer returning `Status::Incomplete("")` is treated as the expected end-of-trace signal, so changes in EOF handling must update the tests. Null referenced-key coverage is targeted at MultiGet data paths but mainly asserts the analyzer completes, not that every emitted human-readable field is semantically correct.

## Test Signals
This file is itself the primary test signal for `block_cache_trace_analyzer`. It validates broad artifact generation, cache simulation miss ratios, timeline accounting, skew and reuse summaries, caller summaries, access-count summaries, GET spatial locality summaries, trace header compatibility, block aggregation by CF/SST/type, and handling of empty MultiGet referenced keys. A passing run indicates that the analyzer can consume traces written by the tracer, produce expected reports, and maintain aggregate state for mixed block types.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_tool.cc -->
# sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_tool.cc

## Purpose
This file is the executable wrapper for the block cache trace analyzer tool. It either reports that gflags is missing or delegates process execution to the analyzer implementation.

## Important APIs, Types, and Functions
When `GFLAGS` is not defined, it includes `<cstdio>` and defines `main()` to print `Please install gflags to run rocksdb tools` to stderr and return `1`. When `GFLAGS` is defined, it includes `tools/block_cache_analyzer/block_cache_trace_analyzer.h` and defines `main(int argc, char** argv)` to return `ROCKSDB_NAMESPACE::block_cache_trace_analyzer_tool(argc, argv)`.

## Control Flow
There is only one branch at compile time. Non-gflags builds fail fast at runtime with a diagnostic. Gflags-enabled builds pass the original command-line arguments through unchanged to the shared tool entry point, and the return value from that function becomes the process exit code.

## State and Persistence Behavior
The wrapper owns no state and performs no file I/O beyond the missing-gflags stderr message. All trace reading, cache simulator config reading, analysis output writing, and flag state live in the delegated analyzer tool implementation.

## Dependencies and Integration Points
The file integrates RocksDB's build system with the reusable `block_cache_trace_analyzer_tool` function. It depends on `GFLAGS` being available for the real analyzer binary and on `ROCKSDB_NAMESPACE` resolving through the included analyzer header. Tests such as `block_cache_trace_analyzer_test.cc` call the same delegated function directly, so this executable and the tests share the true CLI implementation.

## Risks and Edge Cases
Builds without gflags produce a binary that always fails, which is intentional but can surprise users who built only minimal tool dependencies. The wrapper does not install a stack trace handler or perform any argument validation itself; all validation must remain in the delegated tool. Any namespace or signature change to `block_cache_trace_analyzer_tool` breaks this executable.

## Test Signals
There are no local tests for this wrapper. Indirect coverage comes from gflags-enabled builds that link the tool and from analyzer tests that call `block_cache_trace_analyzer_tool` with synthetic argv values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/block_cache_analyzer/block_cache_trace_analyzer_tool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/check_all_python.py -->
# sources/storage-engines/rocksdb/tools/check_all_python.py

## Purpose
This script performs a repository-local Python syntax check. It finds Python files under selected RocksDB directories and compiles each source file with Python's built-in compiler without writing bytecode.

## Important APIs, Types, and Functions
The script uses `glob.glob` to collect filenames and Python's `compile(source, filename, "exec")` to parse and syntax-check each file. It searches the hard-coded base directories `buckifier`, `build_tools`, `coverage`, and `tools`, with depth patterns `*`, `*/*`, and `*/*/*`.

## Control Flow
It initializes an empty `filenames` list, expands the base/depth/suffix patterns for `.py` files, then iterates through every path. For each file it reads the full contents, appends a trailing newline, and calls `compile`. If any file has invalid syntax or cannot be read, Python raises and the script exits nonzero. If all files compile, it prints `No syntax errors in N .py files`.

## State and Persistence Behavior
The script is read-only with respect to the repository. It keeps only an in-memory list of filenames and source strings. Because it uses `compile` directly rather than import machinery, it does not create `.pyc` files and does not execute module top-level code.

## Dependencies and Integration Points
The script depends only on Python 3 standard library functionality and current working directory layout. It is intended as a lightweight pre-commit or post-commit check for Python edits in the RocksDB repo. It intentionally avoids scanning all of `./` to reduce the chance of traversing linked external repositories.

## Risks and Edge Cases
The scan depth is capped at three path components under each base directory, so deeper Python files are skipped. The hard-coded base list misses Python files added elsewhere. Files are opened with default encoding, so non-default encoded sources could fail before compilation. Because files are not sorted or deduplicated, output count and processing order follow glob behavior and may vary by platform. The script catches syntax errors only; import errors, runtime failures, lint issues, and type errors are out of scope.

## Test Signals
The primary signal is the process exit code: zero means all discovered files parsed successfully, while any exception fails the run. The printed count is a useful sanity check that the glob patterns found the expected population.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/check_all_python.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/check_format_compatible.sh -->
# sources/storage-engines/rocksdb/tools/check_format_compatible.sh

## Purpose
This Bash harness builds multiple RocksDB release branches and checks expected storage-format compatibility with a chosen current revision. It covers DB open/verify, compaction, external SST ingestion, backup/restore, and remote compaction service wire-format compatibility across current and historical `*.fb` refs.

## Important APIs, Types, and Functions
The script is configured by command-line argument `ref_for_current` (default `HEAD`) and environment variables `SANITY_CHECK`, `SHORT_TEST`, `LONG_TEST`, `USE_SSH`, `TEST_TMPDIR`, and `J`. It uses Git (`diff-index`, `rev-parse`, `remote`, `fetch`, `checkout`, `reset`, branch deletion), Make (`make clean`, `make ldb`), Docker-independent helper scripts copied from `tools` (`generate_random_db.sh`, `verify_random_db.sh`, `compact_db.sh`, `write_external_sst.sh`, `ingest_external_sst.sh`, `backup_db.sh`, `restore_db.sh`), Python for deterministic input generation, and the built `./ldb` binary.

Key shell functions are `cleanup`, `validate_release_refs`, `invoke_make`, `generate_db`, `compare_db`, `compact_db`, `write_external_sst`, `ingest_external_sst`, `backup_db`, `restore_db`, `member_of_array`, `run_cs_compat_test`, `force_no_fbcode`, and `save_cs_current_ldb`. The release-ref arrays partition compatibility expectations: DB backward-only refs, DB forward-with-options refs, DB forward-no-options refs, external SST backward/forward refs, backup backward/forward refs, and the deduplicated sampled `checkout_refs` list.

## Control Flow
The script first refuses to run with uncommitted changes, resolves the current ref to a hash, records the original branch, sets up a temporary remote pointing at facebook/rocksdb, fetches refs, and installs an EXIT trap that hard-resets, checks out the original branch, deletes the temporary branch, and removes the temporary remote. It creates a test directory under `${TEST_TMPDIR:-/tmp}`, copies current helper scripts into a stable directory so branch checkouts cannot change the harness helpers, and generates deterministic random, sorted, and uniform input data files.

After validating release-ref naming, `SHORT_TEST` truncates each list to its first entry. The script always includes the first release of each list, then either samples or fully includes additional refs depending on `SHORT_TEST` and `LONG_TEST`. It builds the selected current revision on a temporary branch, saves the current `ldb` binary and shared libraries for remote compaction tests, runs a current/current remote compaction smoke test, generates current external SST ingestion data, generates a current DB, and creates a current backup.

For each sampled historical ref, it hard-resets to the fetched ref, patches build detection through `force_no_fbcode`, builds `ldb`, generates an old DB, optionally writes external SSTs, optionally tests old-version ingestion of old and current SSTs, optionally tests opening and compacting current DBs with old binaries, optionally verifies current DBs with options loaded, optionally creates old backups, optionally restores current backups with old binaries, and optionally runs bidirectional remote compaction compatibility between the saved current `ldb` and the old `ldb`.

Finally it rebuilds the current revision, then for each historical ref verifies current can open and compact old DBs, ingest old external SSTs, and restore old backups. It prints a pass message specific to `SANITY_CHECK` or full compatibility mode.

## State and Persistence Behavior
This script intentionally mutates the working copy by checking out and resetting many refs; the initial clean-worktree guard and EXIT cleanup are central to its safety model. It creates all test data under a throwaway test directory and removes any prior instance. It also removes and recreates `$PWD/tmp/cs` as a fallback executable directory if the main temp directory is mounted `noexec`. It saves a copy of the current `ldb` plus nearby shared libraries so current and old binaries can run simultaneously during remote compaction tests. Generated DBs, backups, external SST files, dumps, and compaction-service job directories are transient validation artifacts.

## Dependencies and Integration Points
The harness is tightly integrated with RocksDB's release branch naming scheme, `ldb` command surface, Makefile targets, helper scripts in `tools`, format-version policy, and remote compaction commands (`remote_compaction_primary` and `remote_compaction_worker`). It assumes fetched refs are available from `facebook/rocksdb` over HTTPS or SSH, and that old branches can still be patched enough to build in the current environment. `compact_db.sh` is invoked through the copied helper directory to compact DBs while toggling `try_load_options` and `ignore_unknown_options`.

## Risks and Edge Cases
The script is intentionally destructive to the local checkout during execution; failure of cleanup can leave the repository on a temporary branch or old ref. The clean-worktree guard does not protect untracked files. `git reset --hard`, branch deletion, remote removal, and test-directory `rm -rf` are expected operations, so running this in the wrong repository or with important untracked temp files is risky. Random sampling means default runs may not cover every release; `LONG_TEST=1` is needed for exhaustive coverage, while `SHORT_TEST=1` greatly narrows the matrix. Ancient branches may fail to build due to toolchain drift despite `force_no_fbcode`. Remote compaction tests depend on executable temp storage, shared-library loading, command availability, and background worker cleanup. Helper script semantics are frozen by copying current helpers before checkout, which is useful for stability but can hide old-helper behavior changes.

## Test Signals
A zero exit and `Compatibility Test PASSED` indicate the sampled cross-version matrix passed. `SANITY_CHECK=1` skips builds and helper execution while still exercising syntax, ref validation, checkout flow, and control structure, ending with `check_format_compatible.sh sanity check PASSED`. Failures emit specific `==== Error ... ====` messages from wrapper functions or remote compaction checks, making the failing compatibility lane visible.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/check_format_compatible.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/compact_db.sh -->
# sources/storage-engines/rocksdb/tools/compact_db.sh

## Purpose
This helper compacts a RocksDB database generated by `generate_random_db.sh` using the local `./ldb` binary. It is used by compatibility tests to force a DB rewrite/compaction under a selected RocksDB version.

## Important APIs, Types, and Functions
The script accepts `<DB Path> [if_try_load_options] [if_ignore_unknown_options]`. It builds `extra_params` for `ldb compact` based on `try_load_options`: `"0"` maps to `--try_load_options=false`, `"1"` maps to `--try_load_options=true`, and other values omit the flag. If `ignore_unknown_options` is `"1"`, it appends `--ignore_unknown_options`.

## Control Flow
It validates that at least one argument is provided, assigns defaults of `try_load_options=1` and `ignore_unknown_options=0`, derives optional flags, enables `set -e`, prints the DB path being compacted, and executes `./ldb compact --db=$db_dir $extra_params`.

## State and Persistence Behavior
The script mutates the target RocksDB database by running a compaction through `ldb`. It does not create backups or validate results itself. Its only persistent effect is whatever SST/metadata rewrite the compaction command performs in the DB directory.

## Dependencies and Integration Points
It depends on Bash and an executable `./ldb` in the current working directory. It is copied and invoked by `check_format_compatible.sh` so compatibility runs can compact DBs using the currently checked-out/built version's `ldb`, optionally with options loading disabled or unknown options ignored.

## Risks and Edge Cases
The DB path is passed as `--db=$db_dir` without shell quoting, so paths containing spaces or shell-sensitive characters are unsafe. Non-`0`/`1` values for `try_load_options` silently omit the flag. The script assumes `./ldb compact` semantics are stable across tested versions. Because it uses `set -e`, any `ldb` failure terminates the script and propagates failure to callers.

## Test Signals
The exit status from `./ldb compact` is the only functional signal. Callers such as `check_format_compatible.sh` wrap it and then run DB comparison helpers to verify content after compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/compact_db.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_bench.cc -->
# sources/storage-engines/rocksdb/tools/db_bench.cc

## Purpose
This file is the executable wrapper for RocksDB's `db_bench` benchmark tool. It gates real benchmark execution on gflags availability and delegates to the shared benchmark implementation.

## Important APIs, Types, and Functions
Without `GFLAGS`, it includes `<cstdio>` and defines `main()` to print `Please install gflags to run rocksdb tools` to stderr and return `1`. With `GFLAGS`, it includes `rocksdb/db_bench_tool.h` and defines `main(int argc, char** argv)` to return `ROCKSDB_NAMESPACE::db_bench_tool(argc, argv)`.

## Control Flow
The compile-time `#ifndef GFLAGS` branch selects either a stub executable or a thin delegating executable. In gflags-enabled builds all command-line parsing, benchmark selection, DB setup, workload execution, statistics, and cleanup are performed by `db_bench_tool`.

## State and Persistence Behavior
This wrapper has no benchmark state of its own. In the stub path it only writes an error message. In the real path, all DB files, benchmark state, and output behavior are owned by the delegated benchmark implementation.

## Dependencies and Integration Points
The wrapper integrates the build target named `db_bench` with the reusable API declared in `rocksdb/db_bench_tool.h`. It depends on gflags for the full tool, and on `ROCKSDB_NAMESPACE` for namespace selection. This pattern matches other RocksDB tool wrappers that keep executable `main` functions small while allowing tests or alternate frontends to call the implementation function.

## Risks and Edge Cases
Users can build a nonfunctional stub if gflags is missing. The wrapper performs no preflight checks, stack-trace setup, or argument normalization, so any such behavior must live in `db_bench_tool`. Signature or namespace changes to the benchmark implementation will break this entry point.

## Test Signals
There are no direct tests in this file. Build/link success in a gflags-enabled configuration confirms the wrapper sees `db_bench_tool`, and runtime benchmark tests or smoke runs exercise the delegated implementation. In non-gflags builds the expected signal is exit code `1` with the missing-gflags message.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_bench.cc -->
