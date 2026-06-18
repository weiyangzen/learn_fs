# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wwnr/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_WWNR`, a sample wakeup-while-not-running per-task monitor.

## Important APIs, Types, and Functions

It depends on `RV` and selects `DA_MON_EVENTS_ID`.

## Control Flow

Selecting it builds a standalone per-task sample monitor with ID-aware events.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It integrates directly with RV and scheduler tracepoints in the implementation.

## Risks and Edge Cases

The help text explicitly says the model is broken on purpose to test reactors.

## Test Signals

Kconfig tests should verify ID-aware event support and standalone monitor availability.
