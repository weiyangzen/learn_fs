# sources/distributed-fs/ceph-client/arch/microblaze/kernel/stacktrace.c

Purpose: exposes generic stacktrace collection hooks on top of the MicroBlaze unwinder.

Important APIs and state: `save_stack_trace()` increments skip count to hide helper frames and calls `microblaze_unwind(NULL, trace, "")`; `save_stack_trace_tsk()` unwinds a specific task. Both are GPL-exported.

Control flow: all logic delegates to `unwind.c`; this file only adjusts the caller skip for current-task traces.

State and persistence: mutates the provided `struct stack_trace` counters and entries.

Dependencies and integration: used by generic stacktrace consumers; requires `CONFIG_STACKTRACE` behavior in `microblaze_unwind()`.

Risks and test signals: inaccurate unwinder output propagates to all consumers. Test stack traces for current and sleeping tasks, max entry limits, and skip behavior.
