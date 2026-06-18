# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco.h

## Purpose

This generated header defines the two-state `sco` deterministic automaton.

## Important APIs, Types, and Functions

States are `thread_context` and `scheduling_context`; events are `sched_set_state`, `schedule_entry`, and `schedule_exit`.

## Control Flow

The initial/final state is `thread_context`. `schedule_entry` moves to scheduling context, `schedule_exit` moves back, and `sched_set_state` is valid only in thread context.

## State and Persistence Behavior

The header provides static transition data; per-CPU state is stored by the DA monitor.

## Dependencies and Integration Points

It is included by `sco.c` and interpreted by `rv/da_monitor.h`.

## Risks and Edge Cases

Any mismatch between schedule tracepoint bracketing and actual context can produce false errors.

## Test Signals

Exercise state-set calls around scheduler transitions and check final-state annotations.
