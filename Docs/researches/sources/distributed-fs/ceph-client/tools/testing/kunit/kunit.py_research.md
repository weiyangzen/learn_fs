# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit.py

## Purpose

`kunit.py` is the main command-line frontend for configuring, building, executing, parsing, and reporting Linux KUnit tests. It wraps `kunit_kernel.LinuxSourceTree` for build/run operations, `kunit_parser` for KTAP parsing, and `kunit_json` for optional JSON output.

## Important APIs, Types, And Data

Data types include `KunitStatus`, `KunitResult`, `KunitConfigRequest`, `KunitBuildRequest`, `KunitParseRequest`, `KunitExecRequest`, and `KunitRequest`. Major functions are `config_tests()`, `build_tests()`, `config_and_build_tests()`, `exec_tests()`, `parse_tests()`, `run_tests()`, `tree_from_args()`, command handlers for `run`, `config`, `build`, `exec`, and `parse`, and parser builders `add_common_opts()`, `add_build_opts()`, `add_exec_opts()`, and `add_parse_opts()`. Hidden completion options are `--list-cmds` and `--list-opts`.

## Control Flow

`main()` builds an argparse tree, massages pseudo-boolean flags such as `--json` and `--raw_output`, changes to the kernel root, handles completion listing, then dispatches to the selected subcommand. `run` creates the build directory if needed, configures, builds, executes, and parses. `config` only regenerates `.config`; `build` configures and builds; `exec` runs an already-built kernel and parses/list-tests as requested; `parse` reads stdin or a file and parses saved output. `exec_tests()` also supports listing tests/attributes/suites and isolated per-test or per-suite execution.

## State And Persistence Behavior

Persistent state is mainly in the build directory: `.kunitconfig`, `.config`, `last_used_kunitconfig`, `test.log`, build outputs, and optional JSON result files. `parse` can write JSON to a named file or stdout. The process exits with status 1 on config/build/test failure, making it suitable for CI.

## Dependencies And Integration Points

It depends on Python 3.7+, `argparse`, `os`, `re`, `shlex`, `time`, `kunit_kernel`, `kunit_parser`, `kunit_json`, and `kunit_printer`. It integrates with Linux source layout by deriving the root from `tools/testing/kunit`, with `KBUILD_OUTPUT` for default build directories, with QEMU/UML options, and with shell completion through hidden list options.

## Risks And Edge Cases

The parser uses hidden private argparse internals for option listing. `get_kernel_root_path()` exits if the script path does not contain `tools/testing/kunit`, which can surprise copied or symlinked invocations. `--json` and `--raw_output` require argument massaging to avoid argparse ambiguity. Listing tests uses KUnit executor output filtering and has a comment-level hack to drop a dummy TAP header. Isolated runs can be expensive because each suite/test boots separately.

## Test Signals

Existing tests in `kunit_tool_test.py` cover much of the parser and CLI behavior. Manual validation includes `kunit.py --list-cmds`, `kunit.py run --list_tests`, `kunit.py parse --file <log>`, `kunit.py run --json=stdout`, and failure exit-code checks for broken configs or failing KTAP.
