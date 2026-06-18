# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sssw/sssw.c

## Purpose

This module implements the `sssw` per-task DA monitor, verifying that setting a task sleepable leads to sleeping and that sleeping tasks require wakeup or signal-related transitions.

## Important APIs, Types, and Functions

It uses generated `sssw.h`, `rv/da_monitor.h`, scheduler set-state/switch/wakeup handlers, and a signal-delivery handler.

## Control Flow

On enable, it attaches `sched_set_state_tp`, `sched_switch`, `sched_wakeup`, and `signal_deliver`. Set-state maps `TASK_RUNNING` to runnable and all other states to sleepable. Switch-out classifies preemption, yield, RT-lock blocking, or suspend; switch-in marks runnable execution. Wakeup uses a start event to allow resynchronization into runnable/signal-wakeup paths, and signal delivery resolves signal wakeup state.

## State and Persistence Behavior

State is per task and held in DA storage. It is reset/destroyed by the DA monitor lifecycle.

## Dependencies and Integration Points

It depends on scheduler and signal tracepoints, `rv_trace.h`, and the scheduler container.

## Risks and Edge Cases

Mapping all non-running states to sleepable can be conservative. The code has a special `TASK_RTLOCK_WAIT` blocking case because that state has racy conditions. Signal wakeups are modeled separately to avoid false errors when signals make tasks runnable.

## Test Signals

Exercise blocking sleeps, yields, preemptions, wakeups, signal delivery, and RT lock wait paths while monitoring `event_sssw` and `error_sssw`.
