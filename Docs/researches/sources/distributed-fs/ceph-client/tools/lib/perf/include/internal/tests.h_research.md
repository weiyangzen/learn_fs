<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/tests.h -->
# sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/tests.h

## Purpose
This internal libperf test header provides the lightweight harness used by the C unit tests under `tools/lib/perf/tests`. It centralizes verbose option parsing, start/end status printing, assertion handling, and conditional verbose logging.

## Important APIs, Types, and Functions
- `extern int tests_failed` and `extern int tests_verbose` are shared test-run state defined by `tests/main.c`.
- `get_verbose(char **argv, int argc)` scans for `-v` with `getopt`, returns a boolean-style verbose flag, and resets `optind` so each test function can parse the same argv.
- `__T_START` initializes per-test output, verbosity, and failure count.
- `__T_END` emits `OK` or `FAILED (n)`.
- `__T(text, cond)` records a failure, emits file/line context, and returns `-1` from the caller.
- `__T_VERBOSE(...)` lazily prints verbose detail after inserting a first newline.

## Control Flow and State
Every test function calls `__T_START`, performs checks with `__T`, and closes with `__T_END`. The macros mutate global `tests_failed` and `tests_verbose`; failures short-circuit the current helper by returning `-1`.

## Dependencies and Integration Points
The header depends on libc `stdio.h`, `unistd.h`, and `getopt`. It is included by libperf test sources and is separate from installed public libperf headers.

## Risks and Test Signals
Because `__T` returns from the enclosing function, it is only safe in functions returning `int`. `get_verbose` resets global getopt state, which is deliberate for repeated test entry points but would be surprising outside this harness. The test signal is textual stdout/stderr status plus the final return code from each test function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/include/internal/tests.h -->
