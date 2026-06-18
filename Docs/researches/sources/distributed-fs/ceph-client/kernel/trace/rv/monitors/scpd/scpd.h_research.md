# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd.h

## Purpose

This generated header defines the `scpd` DA model.

## Important APIs, Types, and Functions

States are `cant_sched` and `can_sched`; events are `preempt_disable`, `preempt_enable`, `schedule_entry`, and `schedule_exit`.

## Control Flow

The model starts/finalizes in `cant_sched`. Preempt disable allows scheduling, preempt enable returns to the final state, and schedule entry/exit are valid only while in `can_sched`.

## State and Persistence Behavior

It supplies static state names and transition table; per-CPU runtime state is external.

## Dependencies and Integration Points

It is included by `scpd.c` and DA monitor helpers.

## Risks and Edge Cases

The final state being `cant_sched` means long preemption-disabled sections are non-final but not necessarily erroneous unless invalid events occur.

## Test Signals

Test transition coverage for all four events and invalid schedule-entry without prior preempt-disable.
