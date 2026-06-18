# subset-b-008560 research

Grouped research report for RocksDB buckifier benchmark configuration and helper scripts. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/bench-slow.json -->
# sources/storage-engines/rocksdb/buckifier/bench-slow.json

## Purpose

`bench-slow.json` is the slow ServiceLab/fancy-bench configuration set consumed by `buckifier/buckify_rocksdb.py` when generating RocksDB's `BUCK` file. It describes long-running RocksDB microbenchmark suites that are emitted as slow `fancy_bench_wrapper` targets by `TARGETSBuilder.add_fancy_bench_config`.

The file is a JSON array of 15 configuration objects named `rocksdb_microbench_suite_0` through `rocksdb_microbench_suite_14`. The buckifier appends `_slow` to each generated target name and passes `slow=True`, so the effective Buck target names are `rocksdb_microbench_suite_N_slow`.

## Structure and Important Fields

Each top-level object has the same shape:

- `name`: logical suite name, reused from the fast benchmark file but transformed to a slow Buck target name by the generator.
- `benchmarks`: nested mapping of benchmark binary name to benchmark case name to metric list.
- `expected_runtime_one_iter`: suite-level expected runtime used by the fancy-bench wrapper. Values cluster around 88709 to 88891, much larger than the fast file.
- `sl_iterations`: always `3`, so each ServiceLab run expects three iterations.
- `regression_threshold`: always `10`, expressing the regression threshold passed into the generated wrapper.

The nested `benchmarks` map covers two binaries:

- `db_basic_bench`: present in all 15 suites, with 37 or 38 benchmark cases per suite.
- `ribbon_bench`: present only in suites 8, 9, 11, 12, 13, and 14, with 10 to 13 cases where present.

Whole-file counts from structured inspection:

- 15 top-level suites.
- 631 total benchmark case entries.
- 631 overloaded metric objects containing `est_runtime`.
- Per-case estimated runtimes range from `1.194392` to `8213.664958`.
- Suite expected runtimes range from `88709` to `88891`.

Benchmark families include `DBClose`, `DBGet`, `DBOpen`, `DBPut`, `DataBlockSeek`, `IteratorNext`, `IteratorNextWithPerfContext`, `IteratorPrev`, `IteratorSeek`, `ManualFlush`, `PrefixSeek`, `RandomAccessFileReaderRead`, `SimpleGetWithPerfContext`, and ribbon filter families `FilterBuild`, `FilterQueryNegative`, and `FilterQueryPositive`.

Metric strings include common timing/size fields such as `real_time`, `cpu_time`, `threads`, `db_size`, `get_mean`, `put_mean`, `neg_qu_pct`, `fp_pct`, `seek_ns`, and `size`, plus slow-suite-specific RocksDB internal/perf-context fields such as `block_checksum_time`, `block_read_time`, `block_seek_nanos`, `find_next_user_entry_time`, `flush_time`, `flush_write_bytes`, `get_cpu_nanos`, `get_from_output_files_time`, `get_from_table_nanos`, `get_post_process_time`, `get_snapshot_time`, `internal_key_skipped_count`, `iter_next_cpu_nanos`, `new_table_block_iter_nanos`, and `user_key_comparison_count`.

## Control Flow and Integration

This JSON file has no executable control flow itself. Its operational flow is defined by `buckify_rocksdb.py`:

1. `generate_buck()` opens `buckifier/bench-slow.json`.
2. It parses the array with `json.load`.
3. It walks every suite, binary, benchmark case, and metric value.
4. It strips non-string metric entries by copying only metrics where `not isinstance(metric, dict)`. This removes the per-benchmark `{"est_runtime": ...}` objects from the generated Buck configuration.
5. It calls `BUCK.add_fancy_bench_config(config_dict["name"] + "_slow", clean_benchmarks, True, expected_runtime_one_iter, sl_iterations, regression_threshold)`.
6. `targets_builder.py` formats that data into a `fancy_bench_template` from `targets_cfg.py`.

The case names encode runtime parameters in a slash-separated benchmark-name format, for example `DBGet/comp_style:0/max_data:536870912/per_key_size:1024/...`. These strings are not parsed by the buckifier; they are preserved as keys and interpreted later by the benchmark binary/wrapper.

## State and Persistence

The file is static input data. It persists benchmark suite definitions in source control. At generation time, its contents are copied into generated `BUCK` output, except that per-case `est_runtime` objects are omitted and only string metrics remain in `bench_config`.

No local state is written by the JSON file itself. The persistence side effects happen in the buckifier: opening and rewriting the repository `BUCK` file.

## Dependencies

Direct dependencies are schema-level:

- `buckify_rocksdb.py` expects this file under `repo_path/buckifier/bench-slow.json`.
- Python's `json` module must parse it successfully.
- `TARGETSBuilder.add_fancy_bench_config` must accept the cleaned nested mapping.
- Benchmark binary names must correspond to binaries generated elsewhere, notably `db_basic_bench` and `ribbon_bench`.
- Benchmark case names and metric names must be meaningful to the ServiceLab/fancy bench infrastructure and the underlying RocksDB benchmark executables.

## Risks and Edge Cases

The most important integration risk is in the consumer, not in the JSON: the slow-file loop in `buckify_rocksdb.py` builds `clean_benchmarks` in one loop and then emits all slow configs in a second loop, so the final value from the first loop can be reused for every slow suite. That means all generated slow fancy-bench targets may receive the benchmarks from the last parsed suite while retaining each suite's own name/runtime metadata. This makes this file's per-suite distribution vulnerable to being flattened during BUCK generation.

Other risks:

- The buckifier catches all exceptions around both benchmark JSON files and silently skips fancy-bench generation. A malformed slow JSON file can remove generated benchmark targets without failing the buckifier.
- Per-case `est_runtime` values are deliberately removed before Buck emission. They are useful for curation and balancing but are not preserved in the generated `bench_config`.
- Suite names duplicate the fast file and rely on `_slow` suffixing for uniqueness. Any external consumer that does not mirror the suffix behavior can confuse fast and slow suites.
- The benchmark case keys are long strings with embedded parameters. There is no schema validation for parameter names, numeric ranges, or typo detection.
- Several slow cases are expensive by design, including `ManualFlush` cases around 7.4k to 8.2k estimated runtime and large `max_data:536870912` DB/iterator cases. Accidental promotion into a fast lane would be costly.

## Test Signals

Validation signals available from this repo:

- `jq` successfully parsed the file as JSON.
- Structured inspection found 15 suites, 631 benchmark entries, and the expected top-level fields.
- `check_buck_targets.sh` indirectly tests that this file and `buckify_rocksdb.py` generate a stable `BUCK` file.
- Functional validation requires running the buckifier and checking generated fancy-bench targets, especially that slow suites do not all share the same last-suite benchmark map.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/bench-slow.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/bench.json -->
# sources/storage-engines/rocksdb/buckifier/bench.json

## Purpose

`bench.json` is the fast RocksDB ServiceLab/fancy-bench configuration file used by `buckifier/buckify_rocksdb.py`. It defines shorter microbenchmark suites that are embedded into generated `BUCK` output as non-slow fancy-bench targets.

The file is a JSON array of 15 suites named `rocksdb_microbench_suite_0` through `rocksdb_microbench_suite_14`. Unlike `bench-slow.json`, the buckifier does not suffix the names and passes `slow=False` to `add_fancy_bench_config`.

## Structure and Important Fields

Every suite object contains:

- `name`: generated Buck target/config name.
- `benchmarks`: nested map from binary to benchmark case to metric list.
- `expected_runtime_one_iter`: suite-level expected runtime, mostly `2437` or `2438`, with suites 2 and 11 at `2446`.
- `sl_iterations`: always `3`.
- `regression_threshold`: always `10`.

Whole-file counts from structured inspection:

- 15 top-level suites.
- 149 total benchmark case entries.
- 149 overloaded metric objects containing `est_runtime`.
- Per-case estimated runtimes range from `1.194392` to `696.590699`.
- Two binaries are referenced: `db_basic_bench` and `ribbon_bench`.

`db_basic_bench` appears in all 15 suites. It covers `DBGet`, `DBPut`, `DataBlockSeek`, and `RandomAccessFileReaderRead`. `ribbon_bench` appears in 13 suites and covers `FilterBuild`, `FilterQueryNegative`, and `FilterQueryPositive`.

The metric vocabulary is narrower than the slow file: `real_time`, `cpu_time`, `threads`, `db_size`, `get_mean`, `put_mean`, `neg_qu_pct`, `fp_pct`, `seek_ns`, and `size`.

## Control Flow and Integration

The file is read in the first benchmark-configuration block of `generate_buck()`:

1. Open `repo_path/buckifier/bench.json`.
2. Parse JSON into `fast_fancy_bench_config_list`.
3. For each suite, walk `benchmarks` by binary and benchmark case.
4. Build `clean_benchmarks` by copying only string metrics and dropping dictionary entries such as `{"est_runtime": 510.387506}`.
5. Call `BUCK.add_fancy_bench_config(name, clean_benchmarks, False, expected_runtime_one_iter, sl_iterations, regression_threshold)`.
6. `TARGETSBuilder` pretty-prints the nested map into a generated `fancy_bench_wrapper` target.

The buckifier treats benchmark case keys as opaque strings. Parameterized names such as `DBPut/comp_style:1/max_data:107374182400/per_key_size:256/enable_statistics:1/wal:1/iterations:51200/threads:8` are preserved and passed through to the benchmark runner.

## State and Persistence

The JSON file persists curated fast benchmark suites in source control. It does not write state by itself. During BUCK generation, its cleaned benchmark map and suite metadata are appended to `BUCK`; the per-case `est_runtime` dictionaries are not emitted as metrics.

## Dependencies

Key dependencies and integration points:

- Consumed only when `buckify_rocksdb.py` can find it under `buckifier/bench.json`.
- Requires valid JSON and the expected object schema.
- Depends on generated binaries named `db_basic_bench` and `ribbon_bench`.
- Depends on `TARGETSBuilder.add_fancy_bench_config` and `targets_cfg.fancy_bench_template`.
- The downstream fancy-bench wrapper and benchmark executables must understand the parameterized case names and selected metric names.

## Risks and Edge Cases

- Any schema drift is only caught at buckifier runtime. Because benchmark parsing sits inside a broad `except Exception: pass`, parse or key errors can silently remove all fancy-bench targets.
- `est_runtime` is stored per case but filtered out for generated configs. Runtime balancing logic therefore lives outside the generated target's metric list.
- There is no validation that suite expected runtimes match the sum or max of per-case `est_runtime`; the suite-level `expected_runtime_one_iter` values are manually curated constants.
- The file reuses the same suite-name range as `bench-slow.json`. The fast file relies on the slow file adding `_slow` to avoid target collisions.
- Benchmark case names are manually encoded strings; typos in parameters like `comp_style`, `max_data`, `enable_filter`, or `iterations` would pass JSON validation and only fail or skew measurements later.

## Test Signals

Available validation signals:

- `jq` parsed the file and confirmed 15 suite objects and 149 benchmark case entries.
- The buckifier fast loop emits each suite immediately after cleaning, so per-suite benchmark maps are preserved in generated output.
- `check_buck_targets.sh` can detect when edits to this file require regenerating `BUCK`.
- Meaningful behavioral validation requires generating `BUCK` and inspecting or running the resulting `rocksdb_microbench_suite_N` fancy-bench targets.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/bench.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/buckify_rocksdb.py -->
# sources/storage-engines/rocksdb/buckifier/buckify_rocksdb.py

## Purpose

`buckify_rocksdb.py` is the RocksDB Buck target generator. It reads RocksDB source manifests and benchmark configs, discovers source/test files, and rewrites the repository `BUCK` file through `TARGETSBuilder`.

It is intended to be run from the RocksDB checkout as:

- `python3 buckifier/buckify_rocksdb.py`
- `python3 buckifier/buckify_rocksdb.py '<json dependency map>'`

The optional JSON argument lets callers generate variant test targets with extra dependencies and compiler flags.

## Important APIs, Functions, and Data

- `_EXPORTED_TEST_LIBS = ["env_basic_test"]`: tests that get a dedicated library target before registration, allowing inclusion by other projects.
- `parse_src_mk(repo_path)`: reads `src.mk` and returns a map from make variable name to listed `.c`/`.cc` paths. It treats lines containing `=` as variable starts and lines containing `.c` as file entries.
- `get_cc_files(repo_path)`: recursively discovers `.cc` and `.c` files, skipping roots containing `java`. In this version, the collected list is assigned but not used for target generation.
- `get_non_parallel_tests(repo_path)`: parses `NON_PARALLEL_TEST =` from `Makefile` into a set. In this version, the result is collected but not used when registering tests.
- `get_dependencies()`: returns a default dependency map for the empty target alias, optionally extended from `sys.argv[1]` JSON. Each entry is expected to contain `extra_deps` and `extra_compiler_flags`.
- `generate_buck(repo_path, deps_map)`: main generator that writes libraries, binaries, benchmarks, tests, and exported files.
- `get_rocksdb_path()`: derives the repository path as the parent of the directory containing `sys.argv[0]`.
- `exit_with_error(msg)`: prints an error using `ColorString.error` and exits nonzero.
- `main()`: parses dependency config and runs generation.

The generator depends on `TARGETSBuilder` and `LiteralValue` from `targets_builder.py`, and `ColorString` from `util.py`.

## Control Flow

`main()` calls `get_dependencies()`, computes the RocksDB path, and calls `generate_buck()`.

Inside `generate_buck()`:

1. Print an informational message.
2. Parse `src.mk` into source groups.
3. Discover all C/C++ files and non-parallel tests, though these two data sets are not currently used later.
4. Build `extra_argv` from the optional dependency-map argument for inclusion in the generated file header.
5. Instantiate `TARGETSBuilder("%s/BUCK" % repo_path, extra_argv)`, which immediately truncates and rewrites `BUCK`.
6. Add the oncall marker.
7. Add core library targets:
   - `rocksdb_lib` from `LIB_SOURCES`, `RANGE_TREE_SOURCES`, and `TOOL_LIB_SOURCES`, with header glob and Folly dependencies.
   - `rocksdb_whole_archive_lib` with `link_whole=True`.
   - `rocksdb_with_faiss_lib`.
   - `rocksdb_test_lib`.
   - `rocksdb_with_faiss_test_lib`.
   - `rocksdb_tools_lib`.
   - `rocksdb_cache_bench_tools_lib`.
   - `rocksdb_point_lock_bench_tools_lib`.
   - `rocksdb_stress_lib`.
8. Add binaries:
   - `ldb`
   - `db_stress`
   - `db_bench`
   - `cache_bench`
   - `point_lock_bench`
   - one binary per `MICROBENCH_SOURCES` entry.
9. Validate C test handling: only `db/c_test.c` is supported in `TEST_MAIN_SOURCES_C`; any other C test returns failure.
10. Add the C test wrapper.
11. Try to load `bench.json` and `bench-slow.json`, clean metric lists by removing dict entries, and add fancy-bench configs.
12. Add a generated test section header.
13. Build `test_source_map` from `TEST_MAIN_SOURCES` and `WITH_FAISS_TEST_MAIN_SOURCES`.
14. For each dependency alias and sorted test source, register a test target. Alias variants append `_<alias>` to the target name.
15. For `env_basic_test`, add a dedicated test library and register the test against that library.
16. FAISS tests depend on `:rocksdb_with_faiss_test_lib`; other tests depend on `:rocksdb_test_lib`.
17. Export `tools/db_crashtest.py`.
18. Print generated target counts and return success.

## State and Persistence Behavior

This script rewrites `BUCK` in place. `TARGETSBuilder.__init__` opens the file in binary write mode, so generation starts by truncating any existing `BUCK`. Subsequent builder calls append target stanzas. If generation fails after builder creation, a partial `BUCK` can remain unless the caller, such as `check_buck_targets.sh`, made a backup.

The optional command-line dependency JSON is not persisted separately; it is embedded in the generated header as canonicalized extra argv text and affects generated test target names, dependencies, and compiler flags.

No caches or databases are maintained. All state comes from the repository files (`src.mk`, `Makefile`, benchmark JSON files) and is materialized as generated `BUCK`.

## Dependencies and Integration Points

Source manifests:

- `src.mk`: authoritative source-group manifest for libraries, tests, tools, benchmarks, and optional FAISS sources.
- `Makefile`: source for `NON_PARALLEL_TEST`, although this data is currently unused.

Generator modules:

- `targets_builder.py`: concrete API for appending target stanzas.
- `targets_cfg.py`: templates and Buck macro loads used by the builder.
- `util.py`: colored status output.

Build-system integration:

- Emits Buck macros such as C++ libraries, binaries, unit tests, C test wrapper, fancy bench wrapper, and export file wrapper.
- Hard-codes dependencies on internal targets such as Folly coroutine/container/synchronization libraries and FAISS.
- Reads `bench.json` and `bench-slow.json` to emit fancy-bench configs.
- Used by `check_buck_targets.sh` as the source of truth for whether committed `BUCK` is fresh.

## Risks and Edge Cases

- `BUCK` is truncated at builder construction. Any exception after that point can leave a partial generated file when not wrapped by a backup/restore script.
- `parse_src_mk()` is a simple line parser. It assumes source entries contain `.c`, variable assignments contain `=`, and continuation/file syntax follows the existing `src.mk` pattern.
- `get_cc_files()` and `get_non_parallel_tests()` are computed but unused, which can mislead maintainers into thinking discovery or non-parallel behavior affects generated targets.
- `get_dependencies()` trusts the optional JSON shape. Missing `extra_deps` or `extra_compiler_flags` keys will fail later during test registration.
- The broad benchmark `try/except Exception: pass` hides malformed JSON, missing keys, template failures, or file IO issues. The generator can succeed while silently omitting fancy-bench targets.
- Slow benchmark config generation appears to reuse the final `clean_benchmarks` value for every slow suite because cleaning and emission happen in separate loops. This likely makes every `_slow` generated target use the last slow suite's benchmark map.
- Only `db/c_test.c` is supported in `TEST_MAIN_SOURCES_C`; adding another C test causes generation failure.
- Test target aliases are built by string concatenation (`test + "_" + target_alias`), so aliases should be Buck-name-safe.
- `get_rocksdb_path()` uses `sys.argv[0]`; unusual invocation paths can point generation at the wrong parent directory.

## Test Signals

Primary test signal is deterministic regeneration:

- `buckifier/check_buck_targets.sh` backs up `BUCK`, runs this script, checks `git diff BUCK`, restores the backup, and fails if regeneration changes `BUCK`.

Additional signals:

- Running the script should print generated counts for libraries, binaries, and tests.
- `jq` validation of `bench.json` and `bench-slow.json` helps isolate benchmark parse failures that the script would otherwise swallow.
- A useful regression test would assert that slow fancy-bench configs preserve each suite's own benchmark map instead of all sharing the last map.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/buckify_rocksdb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/check_buck_targets.sh -->
# sources/storage-engines/rocksdb/buckifier/check_buck_targets.sh

## Purpose

`check_buck_targets.sh` is a repository consistency check for generated RocksDB Buck targets. It verifies that the committed `BUCK` file matches the output of `buckifier/buckify_rocksdb.py` and instructs contributors to regenerate rather than hand-edit `BUCK`.

## Control Flow

1. Require a `BUCK` file in the current working directory. If missing, print guidance and exit `1`.
2. Check whether `BUCK` already has uncommitted changes with `git diff BUCK | head -n 1`.
3. If `BUCK` is dirty before the check starts, print that the check is skipped and exit `0`.
4. Copy `BUCK` to `BUCK.bkp`.
5. Run `${PYTHON:-python3} buckifier/buckify_rocksdb.py`.
6. Require that `BUCK` still exists after generation.
7. Check `git diff BUCK | head -n 1` again.
8. If there is no diff, restore `BUCK.bkp` over `BUCK` and exit `0`.
9. If there is a diff, print regeneration instructions and the Python version, restore `BUCK.bkp`, and exit `1`.

## State and Persistence Behavior

The script temporarily writes `BUCK.bkp` in the repository root and rewrites `BUCK` by invoking the buckifier. On normal success and on detected diff failure, it restores the original `BUCK` content from the backup.

It does not use `trap`, so interruption or an unexpected shell/runtime failure after `cp BUCK BUCK.bkp` can leave `BUCK.bkp` behind and may leave generated `BUCK` content in place.

## Dependencies and Integration Points

- Must be run from the RocksDB repository root because it expects `BUCK` and `buckifier/buckify_rocksdb.py` at relative paths.
- Uses `git diff BUCK` to detect dirtiness and generated changes.
- Uses `cp` and `mv` for backup/restore.
- Honors the `PYTHON` environment variable, defaulting to `python3`.
- Depends on `buckify_rocksdb.py` and all of that script's source-manifest and JSON inputs.

## Risks and Edge Cases

- Pre-existing uncommitted `BUCK` changes cause a skip with success status. That avoids overwriting user changes but can let CI miss stale generated targets if the workspace is already dirty.
- The backup restore is duplicated in success/failure branches but not protected by `trap`; termination between generation and restore is unsafe.
- `TGT_DIFF` uses backticks and `[ ! -z "$TGT_DIFF" ]`; it works for this simple check but is less robust than `[[ -n "$TGT_DIFF" ]]`.
- The script only verifies `BUCK`, not benchmark runtime correctness or actual Buck target buildability.
- If the buckifier exits nonzero, `set -e` is not enabled, so the script continues to the post-generation checks. Depending on the partial `BUCK` state, this may still fail by diff, but the original generator error is not surfaced directly.

## Test Signals

The script itself is the main test signal for buckifier determinism. A clean run exits `0` with no generated diff. A stale `BUCK` exits `1` after printing the command to regenerate. Missing `BUCK` also exits `1`.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/check_buck_targets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/rocks_test_runner.sh -->
# sources/storage-engines/rocksdb/buckifier/rocks_test_runner.sh

## Purpose

`rocks_test_runner.sh` is a small Buck test wrapper that creates a temporary test directory under shared memory, runs the provided test command with `TEST_TMPDIR` set to that directory, and removes the directory on success.

## Control Flow

1. Create a temporary directory with `mktemp -d /dev/shm/fbcode_rocksdb_XXXXXXX`.
2. Execute all script arguments as the test command with `TEST_TMPDIR="$TEST_DIR"` in the command environment.
3. If the command succeeds, remove the temporary directory with `rm -rf "$TEST_DIR"`.

The script includes `# shellcheck disable=SC2068` because it intentionally expands `$@` unquoted. That preserves the legacy invocation style but has argument-splitting implications.

## State and Persistence Behavior

The script persists only a temporary directory in `/dev/shm`. Cleanup happens only after successful test execution because the command is chained with `&& rm -rf "$TEST_DIR"`. If the test command fails, crashes, or is interrupted, the temp directory remains for post-failure inspection or later cleanup.

`TEST_TMPDIR` is scoped to the invoked command only; it is not exported for later shell commands except through that environment assignment.

## Dependencies and Integration Points

- Requires `/dev/shm` to exist and allow temporary directory creation.
- Requires `mktemp`.
- Expects callers to pass the actual test command and arguments.
- Integrates with RocksDB tests that honor `TEST_TMPDIR` for temporary database/test files.
- Likely used by generated Buck test rules or macros in the buckifier template stack.

## Risks and Edge Cases

- Unquoted `$@` can split arguments containing spaces or glob characters. This may be intentional for Buck command construction but is fragile for arbitrary commands.
- No `trap` is installed, so interrupts and failures leave the `/dev/shm/fbcode_rocksdb_*` directory behind.
- Cleanup only on success means repeated failing tests can accumulate shared-memory usage.
- If `/dev/shm` is unavailable or too small, the wrapper fails before running the test.
- The script does not propagate cleanup diagnostics; failures are dominated by the test command or `mktemp`.

## Test Signals

Useful validation signals:

- Running `rocks_test_runner.sh true` should create and then remove a temp directory and exit `0`.
- Running it with a failing command should exit nonzero and leave the directory for inspection.
- Tests that rely on RocksDB temp directories should see `TEST_TMPDIR` set to a `/dev/shm/fbcode_rocksdb_*` path.

<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/buckifier/rocks_test_runner.sh -->
