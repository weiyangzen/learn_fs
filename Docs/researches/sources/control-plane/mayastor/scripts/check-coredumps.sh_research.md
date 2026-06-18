# sources/control-plane/mayastor/scripts/check-coredumps.sh

Purpose: CI diagnostic script that reports and fails on new system coredumps.

Important APIs/types/functions: parses `--since DATE`, requires `coredumpctl`, `gdb`, and `jq`, lists coredumps, filters out `sshd` and `udisksd`, and runs `thread apply all bt` in coredump gdb sessions.

Control flow: default since date is very old. For each matching PID from JSON output, it increments a count and attempts a backtrace, tolerating missing core files. Nonzero count exits `1`.

State/persistence: reads systemd coredump journal/storage; writes only stdout/stderr diagnostics.

Dependencies/integration: used by CI after tests to catch crashes not reflected in test exit codes.

Risks: depends on systemd coredump availability and jq despite jq not being preflight-checked. Date parsing is delegated to coredumpctl.

Test signals: no coredumps produces exit `0`; any relevant coredump produces backtraces and exit `1`.
