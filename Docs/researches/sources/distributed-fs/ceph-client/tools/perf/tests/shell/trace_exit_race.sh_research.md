## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_exit_race.sh

Purpose: regression test that `perf trace` does not lose final `exit_group` events from short-lived subprocesses.
Important function: `trace_shutdown_race`.
Control flow: requires perf trace and root, disables user perf config, runs `perf trace --no-comm -e syscalls:sys_enter_exit_group true` ten times appending to a temp file, then counts lines matching the expected timestamp/PID tracepoint regex.
State and persistence: temp output and optional verbose mismatch file are removed.
Dependencies and integration: syscall tracepoint and trace shutdown flushing.
Risks: strict output regex can be affected by config unless `PERF_CONFIG=/dev/null` is honored; test is race-sensitive by design.
Test signals: exactly ten matching exit_group trace lines.
