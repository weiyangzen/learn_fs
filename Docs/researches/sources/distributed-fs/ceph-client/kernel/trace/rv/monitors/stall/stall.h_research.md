# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/stall/stall.h

## Purpose

This generated header defines the `stall` HA automaton.

## Important APIs, Types, and Functions

States are `dequeued`, `enqueued`, and `running`; events are `sched_switch_in`, `sched_switch_preempt`, `sched_switch_wait`, and `sched_wakeup`; environment is `clk`.

## Control Flow

The model starts/finalizes in `dequeued`. Wakeup moves to enqueued, switch-in to running, preempt returns to enqueued, and wait returns to dequeued.

## State and Persistence Behavior

It declares static model data and an environment slot for the jiffy clock; runtime state lives in HA storage.

## Dependencies and Integration Points

It is included by `stall.c` and consumed by `rv/ha_monitor.h`.

## Risks and Edge Cases

Only `dequeued` is final; enqueued/running are expected transient states but final-state consumers should not treat them as immediate errors.

## Test Signals

Transition coverage should verify timer start/cancel behavior around enqueued entry/exit.
