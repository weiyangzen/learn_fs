# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SLEEP`, an RT-app LTL monitor for undesirable sleeps by real-time tasks.

## Important APIs, Types, and Functions

It depends on `RV`, `HAVE_SYSCALL_TRACEPOINTS`, and `RV_MON_RTAPP`; selects `RV_LTL_MONITOR`, `TRACE_IRQFLAGS`, and `LTL_MON_EVENTS_ID`; and defaults enabled.

## Control Flow

Selecting it builds the LTL monitor and required trace event support under the `rtapp` container.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It requires syscall tracepoints, scheduler/lock tracepoints, and IRQ flags tracing. The help text warns of performance impact from `TRACE_IRQFLAGS`.

## Risks and Edge Cases

Production use may be costly due to selected tracing. Architectures without syscall tracepoints cannot build it.

## Test Signals

Kconfig tests should cover syscall tracing and `TRACE_IRQFLAGS` selection.
