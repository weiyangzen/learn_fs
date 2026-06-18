# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SNEP`, checking that scheduling does not enable preemption unexpectedly.

## Important APIs, Types, and Functions

It depends on `RV`, `TRACE_PREEMPT_TOGGLE`, and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting it builds the per-CPU scheduler DA monitor.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It depends on preemption toggle tracepoints and scheduler monitor infrastructure.

## Risks and Edge Cases

The monitor cannot operate without precise preempt toggle visibility.

## Test Signals

Kconfig tests should verify the `TRACE_PREEMPT_TOGGLE` dependency and child registration.
