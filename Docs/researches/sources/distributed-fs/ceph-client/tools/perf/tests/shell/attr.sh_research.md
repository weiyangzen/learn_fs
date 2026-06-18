<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/attr.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/attr.sh

## Purpose

This wrapper runs the Python perf attribute expectation suite against the current `perf` binary.

## Research

The script sets a trap cleanup function, discovers `shelldir` and `perf_path`, then invokes `python "$shelldir/lib/attr.py" -d "$shelldir/attr" -v -p "$perf_path"`. It does not itself inspect output; the Python runner loads attribute expectation files, executes perf with `PERF_TEST_ATTR`, and validates generated event attribute files. State is delegated to `attr.py` temp directories and expected config files. Dependencies are Python, `which perf`, the `attr` expectation directory, and perf's `PERF_TEST_ATTR` instrumentation. Integration is a suite entry point for perf event attribute regression tests. Risks are using `python` rather than `python3` on hosts without a compatible default, and all failure reporting being delegated. Test signal is the Python command exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/attr.sh -->
