# sources/distributed-fs/ceph-client/tools/tracing/rtla/tests/scripts/check-priority.sh

## Purpose

`check-priority.sh` verifies that processes matching a command-name regex have expected scheduler class and priority values according to `chrt -p`.

## Important APIs, Types, and Functions

The script takes three positional arguments: a `pgrep` pattern, expected first `chrt` field value, and expected last `chrt` field value. It uses `pgrep`, `chrt -p`, `cut`, `head`, `tail`, and `grep`.

## Control Flow and Data Flow

It resolves PIDs with `pgrep ^$1`, exits 1 if none are found, loops over each PID, and validates the first and last colon-separated fields from `chrt -p` output. If all checks pass, it prints `Priorities are set correctly`.

## State and Persistence Behavior

The script is read-only and does not modify scheduler state. Its result depends on live process state at the moment it runs.

## Dependencies and Integration Points

It integrates with rtla tests that set tracer or workload priorities and then need an external assertion. It depends on util-linux `chrt` output format.

## Risks and Edge Cases

Unquoted regex input to `pgrep` and grep can surprise callers. `chrt` output format is locale/tool-version sensitive. If a process exits between `pgrep` and `chrt`, the loop may fail. It does not emit detailed diagnostics for which PID failed.

## Test Signals

Tests should run it against known SCHED_FIFO/SCHED_RR/SCHED_OTHER processes and against a missing process name to confirm nonzero failure.
