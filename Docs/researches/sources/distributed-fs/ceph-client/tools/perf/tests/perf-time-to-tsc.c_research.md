<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-time-to-tsc.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/perf-time-to-tsc.c

## Purpose

This selftest verifies that perf mmap metadata can convert between perf time and hardware TSC/counter time while preserving event ordering around two synthetic `COMM` events.

## Research

The file gates support to x86, i386, and arm64. `test__tsc_is_supported` skips unsupported architectures. `test__perf_time_to_tsc` builds a single-thread, online-CPU evlist for `cpu-cycles:u`, sets `comm`, disabled, and no enable-on-exec on each evsel, opens/mmaps, reads `perf_tsc_conversion` from the mmap page, enables events, changes process name to `Test COMM 1`, reads `rdtsc`, changes name to `Test COMM 2`, disables, and scans mmap records for both `COMM` times. It converts the intermediate TSC to perf time and both perf times back to TSC, requiring the intermediate point to fall between them in both domains. State is ring-buffer data and conversion coefficients. Dependencies include TSC support in kernel mmap page, `prctl(PR_SET_NAME)`, parse-events, and PMU availability. Risks include unsupported kernels, hybrid `cpu-cycles` creating multiple evsels, missing comm events, and conversion precision around close timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/perf-time-to-tsc.c -->
