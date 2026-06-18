<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-report -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-report
Purpose: Python failed-syscalls-by-pid wrapper. It parses optional `comm` and invokes `failed-syscalls-by-pid.py`.

Important APIs/types/functions: The executable script is the interface. It delegates to `perf script -s` with a script path derived from `$PERF_EXEC_PATH`; argument parsing is simple shell positional parsing.

Control flow: The wrapper optionally separates report-specific positional arguments from perf options, validates argument count where needed, shifts consumed arguments, and invokes `perf script` with the target analyzer.

State and persistence: The wrapper itself is stateless. It reads the active perf input selected by perf script, usually `perf.data`, and any persistence is owned by the invoked analyzer.

Dependencies and integration points: Depends on `perf script`, `$PERF_EXEC_PATH`, the target Python/Perl analyzer, and a matching perf.data recorded with the paired `*-record` wrapper.

Risks: Argument splitting treats the first token beginning with `-` as the start of perf options, so positional values beginning with `-` cannot be passed unambiguously. Missing `PERF_EXEC_PATH` or missing analyzer scripts will fail at runtime.

Test signals: Run after the paired record wrapper and confirm `perf script` loads the analyzer and produces the expected report header or output format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/bin/failed-syscalls-by-pid-report -->
