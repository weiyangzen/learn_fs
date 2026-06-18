# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snroc/snroc.c

## Purpose

This module implements the `snroc` per-task DA monitor, checking that a task's state is set non-runnable only from its own running context.

## Important APIs, Types, and Functions

It uses generated `snroc.h`, `rv/da_monitor.h`, `handle_sched_set_state()`, and `handle_sched_switch()`.

## Control Flow

On enable, it attaches `sched_set_state_tp` and `sched_switch`. Switch-out starts/resynchronizes the previous task into other context; switch-in transitions the next task into own context. `sched_set_state` is handled for the task passed by the tracepoint.

## State and Persistence Behavior

State is per task and transient. The model starts in `other_context`, then becomes valid own-context after switch-in.

## Dependencies and Integration Points

It depends on scheduler tracepoints, the scheduler container, ID-aware DA trace events, and task identity from tracepoint arguments.

## Risks and Edge Cases

The first state-set event before a task has been observed running may be invalid by design. Switch tracepoint ordering is essential to avoid false positives.

## Test Signals

Exercise task state changes from self and external contexts, context switches, and observe `event_snroc`/`error_snroc`.
