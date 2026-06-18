# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/snep/snep.c

## Purpose

This module implements the `snep` per-CPU DA monitor for "schedule does not enable preempt."

## Important APIs, Types, and Functions

It uses generated `snep.h`, `rv/da_monitor.h`, preempt toggle handlers, and scheduler entry/exit handlers.

## Control Flow

On enable, it attaches preempt disable/enable and scheduler entry/exit tracepoints. Preempt toggles use start events to resynchronize to non-scheduling context, schedule entry transitions into scheduling context, and schedule exit restarts in non-scheduling context.

## State and Persistence Behavior

State is per CPU and transient, resettable through `da_monitor_reset_all`.

## Dependencies and Integration Points

It depends on `trace/events/preemptirq.h`, `trace/events/sched.h`, `rv_trace.h`, and `rv_sched`.

## Risks and Edge Cases

The generated model's state name `scheduling_contex` contains a typo that is user-visible in traces. Resynchronizing on preempt toggles can mask some earlier missed events but avoids persistent desynchronization.

## Test Signals

Run scheduler/preempt stress and inspect `event_snep` and `error_snep` output.
