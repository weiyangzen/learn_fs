# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SNROC`, checking that `sched_set_state` occurs only in the target task's own context.

## Important APIs, Types, and Functions

It depends on `RV` and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_ID`.

## Control Flow

Selecting it builds a per-task DA monitor with ID-aware trace events.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It integrates with scheduler monitor infrastructure and per-task DA event tracing.

## Risks and Edge Cases

Task-context correctness depends on accurate switch-in/out tracepoints.

## Test Signals

Kconfig and runtime smoke tests should verify child registration and ID-aware events.
