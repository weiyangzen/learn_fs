# sources/compression/zstd/tests/cli-tests/run.py

## Purpose
`run.py` is the zstd CLI test runner. It discovers shell test cases, creates isolated scratch directories, runs suite/test setup and teardown hooks, executes each test, and checks stdout, stderr, and exit status against sidecar expectation files.

## Important APIs, types, and functions
The main public structures are `Options`, `TestCase`, and `TestSuite`. `Options` carries environment, timeout, verbosity, preservation, scratch/test paths, and exact-output update mode. `TestCase` owns one executable test file, exposes `launch()`, `analyze()`, and `run()`, and implements `_launch_test()`, `_join_test()`, `_check_exit()`, `_check_output_exact()`, `_check_output_glob()`, and `_analyze_results()`. `TestSuite` is a context manager that runs `setup_once`/`teardown_once`, creates per-test scratch directories, and wraps each test in `setup`/`teardown`.

## Control flow
At startup the script resolves repository paths, parses CLI flags, creates symlinks for zstd-compatible command names under `bin/symlinks`, builds a sanitized environment, and creates `Options`. With no positional tests it calls `get_all_tests()` to walk `test_dir`, filtering helper directories and sidecar files; otherwise it calls `resolve_listed_tests()`. `run_tests()` iterates suites, enters a `TestSuite`, runs sorted unique test files through `test_suite.test_case()`, records pass/fail, and returns a process exit code.

## State, persistence, dependencies, and integration
State is mostly under `TEST_DIR/scratch/`, plus symlinks under `TEST_DIR/bin/symlinks`. Test subprocess environments remove inherited variables beginning with `ZSTD`, then inject paths such as `ZSTD_REPO_DIR`, `DATAGEN_BIN`, `ZSTD_SYMLINK_DIR`, `COMMON`, and `PATH`. Output expectations are file-sidecar contracts: `.stdout.exact`, `.stderr.exact`, `.stdout.glob`, `.stderr.glob`, `.ignore`, and `.exit`. Dependencies include Python 3, POSIX subprocess behavior, `diff`, executable test scripts, and zstd build artifacts.

## Risks and test signals
The runner is intentionally serial despite `TestCase.launch()` supporting asynchronous execution; setup/teardown behavior assumes one test at a time per suite. `_check_output()` currently treats missing expectation files and `.ignore` the same as ignored output, so unanticipated output is not failed unless exact/glob files exist. Timeout exceptions are not caught, so they fail the runner directly. Pass signals are per-test `PASS` lines and final `PASSED all N tests!`; failures include detailed per-check diagnostics and diffs.
