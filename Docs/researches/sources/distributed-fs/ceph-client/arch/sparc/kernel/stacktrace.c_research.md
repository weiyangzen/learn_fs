# sources/distributed-fs/ceph-client/arch/sparc/kernel/stacktrace.c

Purpose: implements SPARC stack trace collection for current and other tasks.

Important APIs/types/functions: `save_stack_trace()` and `save_stack_trace_tsk()` export the generic stacktrace API. `__save_stack_trace()` walks `sparc_stackf`, `pt_regs`, `thread_info`, `kstack_valid()`, `kstack_is_trap_frame()`, and optional function-graph tracer return stacks.

Control flow: for current task it flushes pending stack-trace/ftrace state and reads `%fp`; for other tasks it starts from saved `thread_info->ksp`. It applies `STACK_BIAS`, validates each frame, distinguishes trap frames from normal frames, stops on user trap frames, records caller PCs after `trace->skip`, optionally skips scheduler functions, and repairs function-graph trampoline PCs to original return addresses.

State and persistence: no owned state; it reads kernel stacks and writes caller addresses into caller-provided `stack_trace`.

Dependencies and integration points: used by generic stacktrace/debug code, ftrace function graph tracing, SPARC trap-frame layout, and `kstack.h` validators.

Risks: stack walking must avoid invalid or user frames. Function graph replacement depends on `return_to_handler` and per-task ret-stack indexing. Other-task traces can race with scheduling unless callers observe expected locking/stop conditions.

Test signals: `save_stack_trace()` from current task, blocked-task stack dumps, traces across trap frames, scheduler frame skipping, and function graph tracer enabled/disabled builds.
