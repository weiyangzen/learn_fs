# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/nrp/nrp.h

## Purpose

This generated header defines the `nrp` deterministic automaton model.

## Important APIs, Types, and Functions

States are `preempt_irq`, `any_thread_running`, `nested_preempt`, and `rescheduling`. Events are `irq_entry`, `sched_need_resched`, `schedule_entry`, and `schedule_entry_preempt`. `struct automaton_nrp` stores names, transition table, initial state, and final states.

## Control Flow

The transition table starts at `preempt_irq`; valid paths lead through rescheduling and scheduler-entry states, while preemptive schedule entry from `any_thread_running` is invalid. Only `any_thread_running` is marked final.

## State and Persistence Behavior

The header is static model data. Per-task runtime state is allocated by the DA monitor layer.

## Dependencies and Integration Points

It is included by `nrp.c` after `RV_MON_TYPE` is set and before `rv/da_monitor.h` consumes model symbols.

## Risks and Edge Cases

Because the monitor is generated, enum names and table dimensions must remain synchronized with handler event names. The initial state choice interacts with the C file's start-event shortcut.

## Test Signals

Tests should cover IRQ entry, need-resched, normal schedule, preempt schedule, and final-state trace formatting for ID-aware DA events.
