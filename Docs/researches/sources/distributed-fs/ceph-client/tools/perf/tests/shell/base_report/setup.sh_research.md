<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/setup.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/setup.sh

## Purpose

This setup script prepares perf.data fixtures consumed by the base report tests, including a normal system-wide profile and a latency/context-switch profile.

## Research

The script sources common init, ensures `HEADER_TAR_DIR` exists, records `cpu-clock` with `perf record -asdg` while running `CMD_LONGER_SLEEP`, and validates standard record output patterns. It then records `perf.data.1` with `--latency` using a simple parallel workload that spawns many `cat /proc/cpuinfo` jobs and sleeps. State is `$CURRENT_TEST_DIR/perf.data`, `$CURRENT_TEST_DIR/perf.data.1`, header tar dir, and logs. Dependencies include perf record permissions, software event availability, shell job fan-out, and shared regex patterns. Integration is upstream for `base_report/test_basic.sh`, which assumes these files exist. Risks include permission failures for system-wide recording, low/no samples, host load changing record output, and noisy `cat` logging around the latency setup. Passing signal is both record commands matching standard output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_report/setup.sh -->
