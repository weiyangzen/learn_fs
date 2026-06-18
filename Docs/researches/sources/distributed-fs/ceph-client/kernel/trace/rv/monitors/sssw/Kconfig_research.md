# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SSSW`, checking state-sleep and wakeup relationships.

## Important APIs, Types, and Functions

It depends on `RV` and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_ID`.

## Control Flow

Selecting it builds a per-task scheduler DA monitor.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It integrates with scheduler and signal tracepoints through the implementation.

## Risks and Edge Cases

The property is sensitive to scheduler state distinctions such as yield, preempt, suspend, and RT lock wait.

## Test Signals

Kconfig tests should verify ID-aware event support and scheduler parent dependency.
