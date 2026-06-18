# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/opid/opid.c

## Purpose

This module implements the `opid` per-CPU hybrid automata monitor, verifying that scheduler wakeup and need-resched operations happen with expected IRQ/preemption masking.

## Important APIs, Types, and Functions

The monitor uses `RV_MON_PER_CPU`, generated `opid.h`, and HA callbacks `ha_get_env()`, `ha_verify_guards()`, and `ha_verify_constraint()`. Runtime handlers are `handle_sched_need_resched()` and `handle_sched_waking()`.

## Control Flow

On enable, it initializes the DA/HA monitor and attaches `sched_set_need_resched_tp` and `sched_waking`. Each event uses `da_handle_start_run_event()` against the per-CPU implicit monitor. Guards require interrupts disabled for `sched_need_resched`, and both interrupts disabled and preemption disabled for `sched_waking`.

## State and Persistence Behavior

State is per CPU and trivial because the generated automaton has one state. Environment values are sampled live from `irqs_disabled()` and `preempt_count()`; no state persists after disable.

## Dependencies and Integration Points

It depends on scheduler tracepoints, `rv/ha_monitor.h`, `rv_trace.h`, and `rv_sched`. It compensates for tracepoint-induced preemption disable under `CONFIG_PREEMPTION` by treating preempt count `1` as still enabled at the original event point.

## Risks and Edge Cases

Guard correctness depends on accurately interpreting preempt count around tracepoint execution. Non-preempt kernels always report preemption off. Because the automaton itself never changes state, all useful detection is in environment guards.

## Test Signals

Tests should inspect `error_env_opid` on forced wake/need-resched contexts, compare preempt and non-preempt builds, and validate per-CPU trace output with `event_opid`.
