# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nomiss/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_NOMISS`, the deadline-family monitor that checks deadline entities finish before their deadline.

## Important APIs, Types, and Functions

The symbol depends on `RV`, `HAVE_SYSCALL_TRACEPOINTS`, and `RV_MON_DEADLINE`, defaults to enabled, and selects `HA_MON_EVENTS_ID` so hybrid automata events include entity IDs.

## Control Flow

Selecting the symbol builds the `nomiss` monitor and enables its trace event declarations through `CONFIG_RV_MON_NOMISS`. It is intended as a child of the deadline monitor container.

## State and Persistence Behavior

The Kconfig file holds no runtime state. It controls compile-time availability and trace-event template selection.

## Dependencies and Integration Points

It points users to `Documentation/trace/rv/monitor_deadline.rst` and integrates with the RV, syscall tracepoint, deadline container, and HA monitor-event infrastructure.

## Risks and Edge Cases

The dependency on syscall tracepoints means architectures without syscall tracing cannot build this monitor even if deadline scheduler tracepoints exist. The help text has a minor typo in "deadiline".

## Test Signals

Configuration tests should verify that enabling `RV_MON_DEADLINE` and syscall tracepoints makes `RV_MON_NOMISS` visible, and that disabling any dependency removes it cleanly.
