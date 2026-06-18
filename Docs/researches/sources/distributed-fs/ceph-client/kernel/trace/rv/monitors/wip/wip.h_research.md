# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/wip/wip.h

## Purpose

This generated header defines the `wip` sample automaton.

## Important APIs, Types, and Functions

States are `preemptive` and `non_preemptive`; events are `preempt_disable`, `preempt_enable`, and `sched_waking`.

## Control Flow

The model starts/finalizes in `preemptive`. Preempt disable enters non-preemptive, preempt enable exits it, and `sched_waking` is valid only in non-preemptive state.

## State and Persistence Behavior

Static transition data only; runtime state is per CPU.

## Dependencies and Integration Points

It is included by `wip.c` and DA helpers.

## Risks and Edge Cases

The model is intentionally illustrative and may flag behavior based on simplified preemption observation.

## Test Signals

Transition tests should cover wakeup before/after preempt disable and invalid repeated preempt toggles.
