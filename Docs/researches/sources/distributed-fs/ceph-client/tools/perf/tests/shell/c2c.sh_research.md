<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/c2c.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/c2c.sh

## Purpose

This shell test smoke-tests `perf c2c record` and `perf c2c report` on a workload with memory operations.

## Research

`check_c2c_support` attempts `perf c2c record -- true` to determine hardware/permission availability. `test_c2c_record_report` skips when support probing fails, records `perf test -w datasym 1`, then runs `perf c2c report --stdio` and `perf c2c report -N`. State is one temporary perf.data file and `.old` cleanup. Dependencies are cache-to-cache PMU support, perf c2c command availability, and the `datasym` workload. Integration covers the c2c record/report command path without checking detailed table contents. Risks include skip on most non-supporting hardware, record failure during workload being treated as skip rather than fail, and no validation of specific sharing metrics. Passing signal is successful report generation in both normal and `-N` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/c2c.sh -->
