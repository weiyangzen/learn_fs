# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/scpd/scpd.c

## Purpose

This module implements the `scpd` per-CPU DA monitor for "schedule called with preemption disabled."

## Important APIs, Types, and Functions

It uses `RV_MON_PER_CPU`, generated `scpd.h`, preemptirq tracepoints, scheduler tracepoints, and handlers for preempt disable/enable and schedule entry/exit.

## Control Flow

On enable, DA storage is initialized and four tracepoints are attached. `preempt_disable` moves to `can_sched`; `preempt_enable` restarts the model in `cant_sched`; schedule entry is valid only when scheduling is allowed; schedule exit keeps the monitor in the can-schedule region until preemption is re-enabled.

## State and Persistence Behavior

State is per CPU and transient. `da_monitor_reset_all` resynchronizes the model on global monitoring re-enable.

## Dependencies and Integration Points

The file depends on `trace/events/preemptirq.h`, `trace/events/sched.h`, `rv_trace.h`, and `rv_sched`.

## Risks and Edge Cases

Tracepoint overhead and preemption accounting can affect observed order. Missing preempt toggles would make the automaton stale, which is why Kconfig depends on them.

## Test Signals

Run lockdep/scheduler stress with RV enabled, inspect `event_scpd` transitions, and verify no errors on normal schedule paths.
