# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sco/sco.c

## Purpose

This module implements the `sco` per-CPU DA monitor for scheduling-context operations, checking that `sched_set_state` happens only in thread context.

## Important APIs, Types, and Functions

It uses `RV_MON_PER_CPU`, generated `sco.h`, and `rv/da_monitor.h`. Handlers are `handle_sched_set_state()`, `handle_schedule_entry()`, and `handle_schedule_exit()`.

## Control Flow

On enable, the monitor initializes DA storage and attaches `sched_set_state_tp`, `sched_entry_tp`, and `sched_exit_tp`. A set-state event starts from thread context, scheduler entry transitions into scheduling context, and scheduler exit restarts the monitor in thread context.

## State and Persistence Behavior

State is per CPU in the DA framework. It is reset by `da_monitor_reset_all` and destroyed on disable.

## Dependencies and Integration Points

It depends on scheduler tracepoints, `rv_trace.h`, and the `rv_sched` parent.

## Risks and Edge Cases

Correctness depends on tracepoint ordering around schedule entry/exit. `da_handle_start_event()` on set-state/exit is used to resynchronize if the current model state is unknown.

## Test Signals

Enable under scheduler stress and check for unexpected `error_sco`; targeted tests can invoke state changes inside and outside scheduler context.
