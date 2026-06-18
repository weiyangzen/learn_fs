## sources/distributed-fs/ceph-client/tools/perf/tests/shell/perf-report-hierarchy.sh

Purpose: smoke test for `perf report --hierarchy`.
Important functions: `cleanup`, `trap_cleanup`, and `test_report_hierarchy`.
Control flow: creates a private temp directory, records `uname`, then runs `perf report --hierarchy` against the generated perf.data.
State and persistence: temp directory is path-checked before deletion to reduce cleanup risk.
Dependencies and integration: exercises the report path after `perf record`; no external helper libraries are sourced.
Risks: only verifies command success, not hierarchy content; perf record permission restrictions can fail the test.
Test signals: nonzero command failure aborts under `set -e`; success prints `perf report --hierarchy test [Success]`.
