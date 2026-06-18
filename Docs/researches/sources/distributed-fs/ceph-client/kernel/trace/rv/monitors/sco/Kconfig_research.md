# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_SCO`, a scheduler monitor ensuring `sched_set_state` occurs only in thread context.

## Important APIs, Types, and Functions

It depends on `RV` and `RV_MON_SCHED`, defaults to enabled, and selects `DA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting it builds the per-CPU `sco` automaton and implicit trace events.

## State and Persistence Behavior

The file stores compile-time configuration only.

## Dependencies and Integration Points

It integrates with the scheduler monitor collection and DA implicit event classes.

## Risks and Edge Cases

The monitor assumes scheduler entry/exit tracepoints bracket scheduling context accurately.

## Test Signals

Kconfig and runtime smoke tests should verify the `sco` child appears under `sched`.
