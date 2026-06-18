# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_STS`, a scheduler monitor for relationships between scheduler calls and task switches.

## Important APIs, Types, and Functions

It depends on `RV`, `TRACE_IRQFLAGS`, and `RV_MON_SCHED`, defaults enabled, and selects `DA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting it builds a per-CPU DA monitor consuming IRQ flag, IRQ entry, scheduler entry/exit, and switch tracepoints.

## State and Persistence Behavior

Compile-time configuration only.

## Dependencies and Integration Points

It requires IRQ flag tracing and scheduler monitor infrastructure.

## Risks and Edge Cases

The monitor is sensitive to architecture-specific interrupt tracepoint coverage.

## Test Signals

Kconfig tests should verify `TRACE_IRQFLAGS` gating and child monitor registration.
