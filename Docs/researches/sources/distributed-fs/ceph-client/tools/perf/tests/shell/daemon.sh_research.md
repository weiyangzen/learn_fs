<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/daemon.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/daemon.sh

## Purpose

This shell test validates `perf daemon` lifecycle and control operations: list, reconfig, stop, signal/switch-output, ping, and lock enforcement.

## Research

`check_line_first` and `check_line_other` parse colon-separated `perf daemon -x:` output fields and compare name, run command, base, output, lock/control/ack paths, and uptime. `daemon_start` starts a daemon from a generated config, installs signal cleanup, and polls `perf daemon ping`; `daemon_exit` stops it and waits for the pid. `test_list` checks daemon and session list lines. `test_reconfig` edits the config in place, waits for old sessions to exit and new sessions to start, tests empty config removal, then restores sessions. `test_stop` ensures session processes disappear. `test_signal` sends session/global signals and waits for rotated perf.data files. `test_ping` checks sessions respond OK. `test_lock` verifies a second daemon cannot start on the same base. State is temporary config files, daemon base directories with control/ack/output files, and background perf processes. Dependencies are `perf daemon`, `tail --pid`, `sleep`, and process table visibility. Risks include races in polling, awk colon parsing if paths contain colons, and cleanup on interruption. Passing signal is final `error=0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/daemon.sh -->
