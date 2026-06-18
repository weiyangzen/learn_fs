# sources/distributed-fs/ceph-client/kernel/stacktrace.c

## Purpose
`stacktrace.c` provides generic stack trace collection and formatting wrappers over architecture stack walkers, with fallback support for architectures that still expose legacy `save_stack_trace*()` helpers. It also filters IRQ-stack frames for callers that need to trim traces at interrupt boundaries.

## Important APIs, types, and functions
- Formatting: `stack_trace_print()` and `stack_trace_snprint()` print symbolized entries.
- Collection with `CONFIG_ARCH_STACKWALK`: `stack_trace_save()`, `stack_trace_save_tsk()`, `stack_trace_save_regs()`, optional `stack_trace_save_tsk_reliable()`, and `stack_trace_save_user()`.
- Legacy fallback: weak `save_stack_trace_tsk()` / `save_stack_trace_regs()` warnings and wrappers around `struct stack_trace`.
- Internal `struct stacktrace_cookie` tracks output buffer, size, skip count, and number stored.
- `filter_irq_stacks()` returns the count up to and including the first irq/softirq entry text frame.

## Control flow
Formatting functions iterate the stored addresses and emit `%pS` symbol names. Modern collection initializes a cookie, then calls `arch_stack_walk()` or variants; callback functions skip initial frames and stop when storage fills. Task collection pins the target task stack with `try_get_task_stack()` and drops it afterward. Reliable stack traces delegate validation to `arch_stack_walk_reliable()`. User stack tracing refuses kernel threads and walks from `task_pt_regs(current)`.

## State and persistence behavior
The file stores no persistent state. All state is per-call stack buffers supplied by callers. Task stack references are temporary and refcounted.

## Dependencies and integration points
It depends on scheduler task-stack helpers, kallsyms formatting, interrupt text section symbols, and architecture stackwalk implementations. Exported functions are used by diagnostics, procfs/debugfs, tracing, livepatch/reliability checks, and subsystem error paths.

## Risks
Reliability depends on architecture support; weak fallback emits one-time warnings and cannot guarantee completeness. Callers must size buffers correctly and respect that stack traces can be truncated. Non-current task traces are only safe when the task stack can be pinned, and reliable traces require caller-side inactivity guarantees for non-current tasks.

## Test signals
Build both `CONFIG_ARCH_STACKWALK` and legacy paths, exercise `/proc`/debug stack trace consumers, run livepatch reliable stacktrace tests where available, and verify user stack traces skip kernel threads. `WARN_ON(!entries)` and once-per-boot "not implemented" warnings identify misuse or missing arch support.
