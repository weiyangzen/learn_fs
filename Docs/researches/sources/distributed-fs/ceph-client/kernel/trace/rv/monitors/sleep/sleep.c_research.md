# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/sleep/sleep.c

## Purpose

This module implements the `sleep` LTL monitor, detecting real-time tasks that sleep in latency-dangerous ways while allowing known acceptable sleep/wake patterns.

## Important APIs, Types, and Functions

It uses generated `sleep.h`, `rv/ltl_monitor.h`, atom callbacks `ltl_atoms_fetch()` and `ltl_atoms_init()`, scheduler handlers, lock contention handlers, syscall enter/exit handlers, and `handle_kthread_stop()`.

## Control Flow

On enable, it initializes per-task LTL monitoring and attaches scheduler wake/set-state, lock contention, kthread stop, and syscall tracepoints. `ltl_atoms_fetch()` updates `LTL_RT` using `rt_or_dl_task()`. Initialization clears pulse atoms and classifies kernel threads, migration threads, and RCU tasks. Syscall entry marks clock nanosleep, futex wait/PI-lock, and epoll wait contexts; syscall exit clears those syscall atoms. Scheduler state changes pulse sleep or abort-sleep, wake paths capture wake source and priority, and RT mutex contention marks blocking context.

## State and Persistence Behavior

State is per task in the LTL framework. Pulse atoms represent transient events, while syscall/blocking atoms persist until exit/end handlers clear them. Kernel-thread classification persists in the monitor state and is recomputed at initialization. There is no disk persistence.

## Dependencies and Integration Points

It depends on scheduler, syscall, lock, IRQ context, futex constants, RT/deadline helpers, `rv_trace.h`, and the `rtapp` container.

## Risks and Edge Cases

The source includes a FIXME noting `handle_kthread_stop()` can race with other tracepoint handlers. Correctness depends on matching syscall enter/exit for all relevant sleep syscalls and on priority comparisons in wake context. Kernel-thread name classification for migration/RCU tasks is string based.

## Test Signals

Run RT tasks through futex wait, futex PI lock, epoll wait, absolute clock nanosleep, RT mutex blocking, interrupt/NMI wakes, kthread stop paths, and negative tests for unexpected `error_sleep`.
