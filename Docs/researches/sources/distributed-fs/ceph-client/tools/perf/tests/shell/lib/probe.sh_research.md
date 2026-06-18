<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe.sh

## Purpose

This small shell helper provides skip checks for optional `perf probe` and `perf trace` commands.

## Research

`skip_if_no_perf_probe` runs `perf probe` and returns 2 if stderr/stdout contains `is not a perf-command`. `skip_if_no_perf_trace` runs `perf trace -h` and returns 2 for either `is not a perf-command` or `trace command not available`. State is none. Dependencies are user PATH resolving the intended perf binary and command help/error wording. Integration lets shell tests conditionally skip when perf was built without probe or trace support. Risks include localized or changed diagnostic messages, checking the default `perf` rather than `CMD_PERF`, and returning 0 for commands that exist but fail later due to permissions. Test signal is return code 2 for unavailable commands and 0 otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe.sh -->
