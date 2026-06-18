# sources/distributed-fs/ceph-client/arch/um/kernel/stacktrace.c

## Purpose
Implements stack walking and reliable stack trace capture for UML tasks.

## Important APIs, Types, and Functions
`dump_trace()` scans from the current stack pointer to the thread-stack end, recognizes kernel text addresses, and marks entries reliable when they align with the frame pointer chain. `save_stack_trace()` and `save_stack_trace_tsk()` collect reliable entries through `dump_ops` and export GPL symbols.

## Control Flow, State, and Persistence
The walker uses transient stack contents, optional `tsk->thread.segv_regs`, and frame-pointer state. It stores addresses only in the caller-provided `struct stack_trace`; no global state persists.

## Dependencies and Integration Points
Uses UML stack pointer/frame pointer helpers in `asm/stacktrace.h`, `__kernel_text_address()`, and generic stacktrace APIs. `sysrq.c` uses `dump_trace()` for printable call traces.

## Risks and Test Signals
Risks include unreliable traces when frame pointers are absent/corrupt and reading stale stack slots during faults. Test sysrq stack dumps, WARN/OOPS traces, KASAN/fault paths, and stack traces for non-current tasks.
