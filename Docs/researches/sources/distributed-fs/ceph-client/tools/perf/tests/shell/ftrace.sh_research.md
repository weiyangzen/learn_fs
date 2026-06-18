<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/ftrace.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/ftrace.sh

## Purpose

This root-only shell test validates `perf ftrace` list, trace, latency, and profile subcommands using `sleep 0.1`.

## Research

The script skips unless running as root. `test_ftrace_list` runs `perf ftrace -F`, stores sleep-related syscall functions, and prints them. `test_ftrace_trace` runs graph tracing for sleep, requires comment lines and `sleep()`, then selects a syscall function observed in trace output. `test_ftrace_latency` runs latency tracing for that function and checks header/summary markers. `test_ftrace_profile` runs profile mode and uses a regex to find a `clock_nanosleep` line with count 1 and about 0.1 seconds. State is a temporary output file and selected `target_function`. Dependencies are ftrace permissions, tracefs, syscall naming, and architecture-specific function prefixes. Risks include root requirement, sleep syscall naming changes, timing variance, and ftrace conflicts with existing tracing. Passing signal is all grep checks succeeding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/ftrace.sh -->
