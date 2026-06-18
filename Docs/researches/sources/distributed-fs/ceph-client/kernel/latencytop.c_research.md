# sources/distributed-fs/ceph-client/kernel/latencytop.c

## Purpose
`latencytop.c` records scheduler sleep latencies for system-wide and per-task reporting used by the latencytop userspace tool.

## Important APIs, Types, And Functions
Global state includes `latency_record[MAXLR]`, `latency_lock`, and `int latencytop_enabled`. Public functions are `clear_tsk_latency_tracing()` and scheduler-called `__account_scheduler_latency()`. Procfs uses `lstats_show()`, `lstats_write()`, and `lstats_proc_ops`; sysctl uses `kernel/latencytop`.

## Control Flow
When enabled scheduler code calls `__account_scheduler_latency()` with a task, duration, and interruptible flag. Long interruptible waits over 5 ms, zero, and negative durations are ignored. The function captures a stack trace, merges it into the global table for user tasks and into the task-local table, or drops it when fixed-size arrays are full. `/proc/latency_stats` reads formatted counters and symbolized backtraces; writing clears global stats.

## State And Persistence
Latency data is in fixed-size in-memory arrays and persists until overwritten by matching records or cleared. Per-task records live in `task_struct`; global records live for the kernel lifetime. Enabling the sysctl also forces schedstats on.

## Dependencies And Integration Points
The file depends on scheduler latency accounting, stacktrace capture, kallsyms symbol formatting, procfs seq files, sysctl, raw spinlocks, and task-local latency fields.

## Risks And Edge Cases
Fixed arrays drop new causes once full, so userspace must clear regularly. Stack trace identity is pointer-based and can be affected by module unload or symbol visibility. Locking is global and IRQ-saving, so accounting cost matters in scheduler paths.

## Test Signals
Signals include sysctl enabling and schedstat forcing, `/proc/latency_stats` header and rows, write-to-clear behavior, per-task clearing, dropped long interruptible sleeps, and merged counts/max/total for repeated backtraces.
