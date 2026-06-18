# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SCPD`, checking that `schedule()` is called with preemption disabled.

## Important APIs, Types, and Functions

It depends on `RV`, `TRACE_PREEMPT_TOGGLE`, and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting it builds a per-CPU DA monitor that consumes preempt toggle and scheduler entry/exit tracepoints.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It requires preemption tracepoints and scheduler monitor infrastructure.

## Risks and Edge Cases

Without `TRACE_PREEMPT_TOGGLE`, the model cannot observe preempt-disable state changes.

## Test Signals

Kconfig tests should verify dependency gating on `TRACE_PREEMPT_TOGGLE`.
