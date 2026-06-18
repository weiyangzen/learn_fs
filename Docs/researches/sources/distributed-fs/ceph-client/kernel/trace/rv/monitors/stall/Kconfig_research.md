# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_STALL`, a sample HA monitor that identifies tasks stalled longer than a threshold.

## Important APIs, Types, and Functions

It depends on `RV` and selects `HA_MON_EVENTS_ID`.

## Control Flow

Selecting it builds a standalone per-task HA sample monitor with ID-aware events.

## State and Persistence Behavior

Only compile-time configuration is held.

## Dependencies and Integration Points

It integrates directly with RV rather than a container and points to `Documentation/trace/rv/monitor_stall.rst`.

## Risks and Edge Cases

As a sample monitor, default thresholds and semantics may be illustrative rather than production policy.

## Test Signals

Kconfig tests should verify standalone availability with `RV` and HA ID event selection.
