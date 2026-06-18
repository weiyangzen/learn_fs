# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/Kconfig

## Purpose

This Kconfig entry exposes `RV_MON_OPID`, a scheduler monitor checking that operations such as wakeup and need-resched occur with interrupts and preemption disabled.

## Important APIs, Types, and Functions

The symbol depends on `RV` and `RV_MON_SCHED`, defaults to enabled, and selects `HA_MON_EVENTS_IMPLICIT`.

## Control Flow

Selecting the symbol builds the per-CPU hybrid automata monitor and its implicit-ID trace events.

## State and Persistence Behavior

The file contains compile-time configuration only.

## Dependencies and Integration Points

It integrates with the scheduler monitor container, HA monitor framework, and documentation for scheduler RV monitors.

## Risks and Edge Cases

It requires reliable IRQ/preempt state sampling at tracepoint time; that semantic dependency is not visible in Kconfig.

## Test Signals

Build matrix coverage should verify event class selection and dependency gating through `RV_MON_SCHED`.
