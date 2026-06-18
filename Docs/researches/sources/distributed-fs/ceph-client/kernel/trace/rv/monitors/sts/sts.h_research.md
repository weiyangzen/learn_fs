# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sts/sts.h

## Purpose

This generated header defines the `sts` scheduler/task-switch automaton.

## Important APIs, Types, and Functions

States are `can_sched`, `cant_sched`, `disable_to_switch`, `enable_to_exit`, `in_irq`, `scheduling`, and `switching`. Events are `irq_disable`, `irq_enable`, `irq_entry`, `sched_switch`, `schedule_entry`, and `schedule_exit`.

## Control Flow

The model starts/finalizes in `can_sched`. Schedule entry enters scheduling, IRQ disable moves toward a required switch, switch then requires IRQ enable before exit, and IRQ entry has dedicated transitions.

## State and Persistence Behavior

The header stores static transition data only; runtime state is per CPU in DA storage.

## Dependencies and Integration Points

It is consumed by `sts.c` and DA monitor helpers.

## Risks and Edge Cases

The model encodes strict event ordering; small tracepoint reorderings can surface as monitor errors.

## Test Signals

Transition tests should cover scheduler entry/exit with and without switches, interrupt entry during disabled sections, and invalid switch outside scheduling.
