# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_WIP`, a sample wakeup-in-preemptive per-CPU monitor.

## Important APIs, Types, and Functions

It depends on `RV` and `TRACE_PREEMPT_TOGGLE`, selects `DA_MON_EVENTS_IMPLICIT`, and has no scheduler-container dependency.

## Control Flow

Selecting it builds a standalone per-CPU DA monitor using preempt toggle and wakeup tracepoints.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It integrates with RV, preempt toggle tracepoints, and scheduler waking tracepoints.

## Risks and Edge Cases

The help text notes the monitor illustrates a limitation of preempt disable/enable events, so it is primarily a sample.

## Test Signals

Kconfig tests should verify standalone availability and dependency on `TRACE_PREEMPT_TOGGLE`.
