# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_NRP`, a scheduler monitor checking that preemption follows `need_resched` expectations.

## Important APIs, Types, and Functions

The symbol depends on `RV` and `RV_MON_SCHED`, defaults to enabled except on ARM64, and selects `DA_MON_EVENTS_ID` for per-task event tracing.

## Control Flow

When enabled, the monitor is built as a child of the scheduler monitor collection. The default exclusion on ARM64 reflects known instability on that architecture.

## State and Persistence Behavior

State is compile-time configuration only. Runtime per-task DA state is in `nrp.c`.

## Dependencies and Integration Points

It integrates with the scheduler monitor container and RV DA event configuration. The help text references `Documentation/trace/rv/monitor_sched.rst`.

## Risks and Edge Cases

Users can still force-enable it on ARM64 for testing, so runtime behavior should be treated cautiously there.

## Test Signals

Kconfig matrix tests should cover x86/default enabled, ARM64 default disabled, and dependency gating through `RV_MON_SCHED`.
