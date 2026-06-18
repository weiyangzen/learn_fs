# sources/storage-engines/wiredtiger/test/evergreen.yml lines 1-7779

## Scope

This chunk covers almost the entire WiredTiger Evergreen project configuration: global task hooks, reusable Evergreen functions, shared variable anchors, the full visible `tasks:` catalog, and `buildvariants:` from `ubuntu2004` through the start of `amazon2023-arm64-msan`. The source file has 7,839 lines; this chunk stops at line 7,779 while the `amazon2023-arm64-msan` buildvariant is still being declared, so later lines must be consulted for the end of that variant and any following variants.

## Purpose

The file is the CI contract for WiredTiger in Evergreen. It maps source checkout, build configuration, compilation, test execution, artifact movement, diagnostics, statistics publishing, and platform selection into Evergreen primitives. Rather than implementing application logic, it composes shell scripts and repository tools into a large scheduler matrix.

The top-level settings enable `stepback`, establish `pre` cleanup/environment setup, define `post` diagnostic and upload hooks, and install a timeout hook that invokes the WiredTiger hang analyzer. The default execution timeout is six hours, with specific tasks overriding it for stress, memory-model, coverage, and long performance jobs.

## Important Evergreen Surfaces

### Global Hooks

- `pre` always runs `cleanup` and `setup environment`, so task bodies can assume a fresh checkout location and common expansions such as `PREPARE_TEST_ENV` and `PREPARE_PATH`.
- `post` uploads stack traces, format configs, model workloads, stderr/stdout, stat files, generic task artifacts, and hang-analyzer outputs. This makes failed test homes and diagnostics persistent in S3.
- `timeout` runs `run wt hang analyzer`, which collects core/debugger output from `wiredtiger/cmake_build` when a task stops making progress.

### Functions

The `functions:` block is the primary API surface. Important reusable functions include:

- Environment and project setup: `setup environment`, `get project`, `generate github token`, `get automation-scripts`, `checkout develop`, `get engflow creds`.
- Build functions: `configure wiredtiger`, `python config check`, `make wiredtiger`, `compile wiredtiger`, `compile wiredtiger develop`, `compile mongodb`, `compile wiredtiger docs`.
- Artifact movement: `fetch artifacts`, `fetch endian format artifacts`, `upload artifact`, `upload artifact for compatibility test`, `upload wtperf test artifact`, `upload endian format artifacts`, `upload stacktraces`, `upload stat files`.
- Test wrappers: `make check directory`, `make check all`, `unit test`, `unit test tsan parallel`, `format test`, `format test script`, `format test disagg`, `checkpoint test`, `checkpoint stress test`, `cppsuite test`, `cppsuite perf test`, `csuite test`, `model test`, `run-perf-test`, `run workgen test`.
- Reporting and metrics: `code coverage analysis`, `run code coverage tests`, `code coverage publish report`, `code coverage publish main page`, `upload stats to atlas`, `upload stats to evergreen`, `validate-expected-stats`, `tsan warning metric`.
- Integration helpers: `fetch mongo repo`, `import wiredtiger into mongo`, `fetch mongo-tests repo`, `build and push antithesis container`, `verify wt datafiles`, `verify wt datafiles with binary`.

These functions use Evergreen expansion syntax heavily. Values such as `${build_variant}`, `${revision}`, `${build_id}`, `${execution}`, `${dependent_task|compile}`, `${CMAKE_BUILD_TYPE|}`, and `${num_jobs}` form the implicit parameter interface between variants, tasks, and shell scripts.

### Variable Anchors and Templates

The `variables:` section defines YAML anchors reused by tasks and variants:

- Built-in extension flags set CMake options for LZ4, Snappy, Zlib, and Zstd.
- Static-library anchors toggle `ENABLE_SHARED` and `ENABLE_STATIC`.
- Sanitizer anchors set ASan build type, clang preset, cppsuite disabling, and tcmalloc exclusion.
- The macOS template supplies Xcode clang, Homebrew LLVM environment, dyld library path, and a standard task list.
- Stress-test templates define repeated task shapes for format stress, ASan stress, race-condition stress, recovery stress, disaggregated format stress, and workgen tests.

The anchors make the task catalog compact but create a dependency between template changes and many task names produced later via YAML merge (`<<: *anchor`).

## Control Flow

The common task flow is:

1. Checkout `wiredtiger` with `git.get_project`.
2. Configure with CMake through `configure wiredtiger`.
3. Build with Ninja, Make, or the Windows PowerShell helper through `make wiredtiger`.
4. Either upload the complete build as `wiredtiger.tgz` or run tests directly.
5. Dependent test tasks fetch the compile artifact from S3 and run in the extracted `wiredtiger` tree.
6. Post hooks collect stack traces, configs, stat files, stdout/stderr, and task artifacts regardless of the specific task body.

Compilation control flow branches on OS and variant settings. Windows calls `test/evergreen/build_windows.ps1`; macOS injects Python library/include paths discovered through `find_libpython`; Linux prefers CMake presets when `CMakePresets.json` exists and otherwise falls back to explicit `CC` and `CXX`. TCMalloc is installed or downloaded only when `ENABLE_TCMALLOC=1`, and sanitizer builds explicitly disable it.

Test control flow is mostly task-selected. `make check all` invokes CTest labels, `unit test` builds include/exclude lists from fail-list files before calling `test/suite/run.py`, `unit test tsan parallel` uses `tools/pytest_parallel`, format tests execute either `test/format/t` or `format.sh`, cppsuite tasks run from `cmake_build/test/cppsuite`, and perf tasks run `bench/perf_run_py/perf_run.py` twice to produce both Evergreen and Atlas JSON outputs.

Buildvariants then select task subsets by name, tag expression, distro override, `batchtime`, `cron`, and variant-local expansions. For example, Ubuntu 20.04 runs broad PR, lint, long, compatibility, workgen, model, and live-restore coverage; sanitizer variants narrow the matrix and inject sanitizer options; non-standalone variants add `WT_STANDALONE_BUILD=0` and unit-test hooks; ARM64/Amazon variants repeat major coverage on different host pools.

## State and Persistence Behavior

Persistent state is almost entirely external to this YAML and mediated through Evergreen expansions and S3:

- Compile tasks upload build artifacts under `wiredtiger/${build_variant}/${revision}/artifacts/${task_name}_${build_id}${postfix|}.tgz`.
- Test tasks fetch compile or data artifacts by `dependent_task`, build variant, revision, build id, and optional postfix.
- Format configs, model workloads, stack traces, stat files, hang-analyzer outputs, coverage reports, perf JSON, WT_TEST homes, datafiles, and compatibility directories are uploaded for later inspection.
- Long performance tests intentionally persist populated WT homes and backups for downstream no-create or live-restore tasks.
- Documentation update tasks clone `wiredtiger.github.com`, rsync generated docs by branch, commit changes as the doc bot, and push through a generated GitHub App credential.
- Atlas/Evergreen metrics upload functions persist performance, code coverage, complexity, modularity, and TSAN-warning records with task metadata.

Transient local state includes `wiredtiger/`, `mongo/`, `mongo-tests/`, `automation-scripts/`, virtualenvs, `cmake_build`, `WT_TEST*`, temporary fail-list files, and coverage build directories. The `cleanup` function removes `wiredtiger` and `wiredtiger.tgz`, but many task-specific directories are intentionally archived before cleanup.

## Dependencies and Integration Points

Key external dependencies include Evergreen commands (`git.get_project`, `expansions.update`, `s3.get`, `s3.put`, `archive.targz_pack`, `subprocess.exec`, `github.generate_token`, `timeout.update`), AWS/S3 credentials, GitHub token generation, MongoDB toolchain v5, CMake, Ninja/Make, Python 3.11/3.13 depending on platform, virtualenv, pip packages, Bazel/EngFlow credentials for MongoDB integration, and platform-specific hosts such as Windows 2022, macOS 14 ARM64, RHEL 8, Ubuntu 20.04/22.04, zSeries, PPC, Amazon 2023 ARM64.

Repository integration is broad. The YAML delegates behavior to many checked-in scripts and tools, including `test/evergreen/*`, `test/suite/run.py`, `tools/pytest_parallel`, `bench/perf_run_py/*`, `bench/workgen/runner/*.py`, `test/format/*`, `test/cppsuite`, `test/csuite`, `test/compatibility/*`, `dist/s_all`, `dist/s_docs`, `dist/s_release`, `dist/modstat`, `tools/antithesis`, and MongoDB/mongo-tests repositories for integration and large-scale tests.

The file also integrates with Evergreen task tagging. Tags such as `pull_request`, `python`, `unit_test`, `unit_test_xsan`, `unit_test_tsan`, `unit_test_disagg`, `cppsuite-stress-test`, `cppsuite-perf-test`, `stress-test-*`, `stress-test-disagg`, `data-validation-stress-test`, `model_checking`, `workgen-test`, `pull_request_code_statistics`, and perf category tags are the main grouping mechanism for variant task selection.

## Task Families and Test Signals

The visible task catalog provides several distinct quality signals:

- Build and compiler coverage: default compile, develop compile, static/dynamic production toggles, GCC/Clang version sweeps, uncommon build flags, configure-combinations, minimal-extension builds, static WT utility validation.
- CMake/CTest coverage: make-check-all, per-directory tests for examples, checkpoint, cursor order, fops, format, huge, manydbs, packing, readonly, salvage, thread, wtperf, catch2, and csuite labels.
- Python suite coverage: normal buckets, long buckets, XSAN buckets, random-seed tests, hook tests for timestamp, tiered, timing stress, parallel checkpoint, disaggregated leader/follower/table-prefix/key-provider, TSAN-specific parallel runs, and macOS Python config validation.
- Stress coverage: format stress, format predictable replay, schema abort predictable replay, checkpoint stress, recovery stress, split/skiplist stress, data validation checkpoint matrix, disaggregated leader/follower/switch modes, abort recovery, race-condition ASan, PPC/zSeries-specific format stress.
- Compatibility and persistence coverage: release compatibility tests, upgrade/daily/weekly/patch/import modes, compatibility against develop, endian datafile generation/verification across little/big-endian variants, WT datafile verification with different binaries.
- Coverage/statistics: parallel code coverage buckets, merged coverage report, per-test coverage, Catch2 coverage, code-change PR report, cyclomatic complexity, modularity metrics, TSAN warning metrics.
- Performance: wtperf btree/oplog/checkpoint/stress/eviction/log/YCSB tests, long 500m btree workflows, live-restore perf, cppsuite perf, disaggregated failover perf, many-dhandle stress, prefetch verify microbenchmarks, workgen tests, and wt2853 perf tests.
- Integration: MongoDB many-collection test using imported WiredTiger, docs compile/update, package task, Antithesis container build/push.

## Risks and Maintenance Concerns

- The YAML is a single large scheduler specification. Small expansion or anchor changes can affect many tasks and variants through YAML merges and tag expressions.
- Many shell snippets rely on Evergreen expansion defaults. Empty expansions can change command-line shape; the `unit test` function already works around this by copying `${unit_test_ignore}` into a local variable before testing `-n`.
- Artifact names couple producers and consumers through `build_variant`, `revision`, `build_id`, `dependent_task`, and `postfix`. Renaming compile tasks, changing postfixes, or moving upload paths can break downstream fetches.
- Sanitizer behavior is fragile. Comments call out hidden ASan/TSan warnings under parallel execution, TSAN deadlock false positives, MSAN false positives from uninstrumented libraries, and sanitizer/tcmalloc incompatibility.
- Platform-specific branches are dense: Windows uses PowerShell and Cygwin paths, macOS constructs Python library paths manually, RHEL PPC strips ZSTD and disables mmap in some format runs, big-endian variants disable ZSTD, and Amazon/Ubuntu ARM64 variants override distros.
- Some buildvariant task references in this chunk name `generate-tsan-metric-timestamp` and `generate-tsan-metric-disagg-timestamp`, but those task definitions are not visible in lines 1-7779. They may appear after the chunk, be generated elsewhere, or be stale references; the merge lane should verify the complete file.
- The chunk ends mid-`amazon2023-arm64-msan` buildvariant, so any conclusions about that variant's task list are incomplete until the following chunk is merged.
- Several tasks intentionally ignore failures or alter expected failures for coverage or sanitizer collection. This is useful for metrics but can obscure task health if propagated to the wrong variant.
- Documentation update and Atlas upload tasks handle secrets; several functions avoid verbose mode or use `silent: true`, but changes to logging could expose credentials.

## Research Notes for Merge Lane

This chunk establishes the high-level structure and almost all names needed by a final per-file report. The merge lane should combine this with the trailing chunk to confirm the complete buildvariant list, especially the rest of `amazon2023-arm64-msan`, `amazon2023-arm64-ubsan`, and `amazon2023-stress-nonstandalone`, which are only partially or not fully covered by this line range.
