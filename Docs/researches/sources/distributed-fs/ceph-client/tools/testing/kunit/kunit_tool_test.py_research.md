<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_tool_test.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_tool_test.py

## Purpose

`kunit_tool_test.py` is the unit test suite for the KUnit Python command-line tooling. It exercises Kconfig parsing, KTAP/TAP parsing, parser laziness, Linux source-tree setup and QEMU/UML execution paths, JSON export, CLI argument plumbing, raw-output modes, timeout/build-directory handling, filter/list behavior, and isolated test execution.

## Important APIs, Types, and Functions

The file uses `unittest` and `unittest.mock` heavily. `setUpModule()` creates a temporary directory and locates `test_data`; `tearDownModule()` removes the temporary directory. `_test_data_path()` resolves fixture logs and configs. Test classes are `KconfigTest`, `KUnitParserTest`, `LineStreamTest`, `LinuxSourceTreeTest`, `KUnitJsonTest`, and `KUnitMainTest`. `line_stream_from_strs()` adapts lists to `kunit_parser.LineStream`, and `StrContains` lets mock assertions match substrings.

## Control Flow

The suite first validates low-level Kconfig read/write/subset semantics, then parses many fixture logs for success, failure, skipped suites, missing plans, no tests, kernel panic, prefixed printk output, KTAP attributes, and late test plans. Source-tree tests construct `LinuxSourceTree` with temporary config files and patched operations to avoid real kernel builds. CLI tests patch `kunit_kernel.LinuxSourceTree`, feed `kunit.main()` command arrays, and assert calls into `build_reconfig()`, `build_kernel()`, `run_kernel()`, and list helpers.

## State and Persistence Behavior

Persistent state is only temporary test data: `test_tmpdir`, temporary `.config`/`.kunitconfig` files, mocked environment variables, and generated output files such as KUnit run logs inside temporary build directories. The tests intentionally clear `os.environ` in main CLI tests and mock signal handling so host state does not leak into assertions.

## Dependencies and Integration Points

The suite imports `kunit_config`, `kunit_parser`, `kunit_kernel`, `kunit_json`, `kunit`, and `kunit_printer.stdout`. It integrates with fixture logs under `tools/testing/kunit/test_data`, Python subprocess behavior, terminal reset via `stty sane`, `KBUILD_OUTPUT`, QEMU argument handling, kernel argument forwarding, `--alltests`, `--kconfig_add`, `--run_isolated`, `--list_suites`, and `--list-opts`.

## Risks and Edge Cases

Tests depend on fixture log exactness and on mock call signatures matching production request dataclasses. Because many assertions check only plumbing, they can miss behavior inside patched dependencies. Raw-output tests assert absence of summary messages rather than full output fidelity. The terminal reset tests are careful to avoid invoking `stty` on non-TTY stdin; regressions there can corrupt interactive sessions.

## Test Signals

Running this file directly or through `run_checks.py` should pass without a kernel build except for code paths intentionally mocked. Strong signals include parser status/count assertions, JSON status mappings for FAIL/ERROR/SKIP/PASS, source-tree config conflict errors, non-mutating run-kernel args, correct `KBUILD_OUTPUT` defaulting, and isolated-suite/test calls derived from listed tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_tool_test.py -->
