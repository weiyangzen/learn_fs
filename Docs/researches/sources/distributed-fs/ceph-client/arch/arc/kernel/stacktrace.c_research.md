# sources/distributed-fs/ceph-client/arch/arc/kernel/stacktrace.c

Purpose: provides ARC stack trace APIs as thin wrappers around the DWARF2 unwinder. It feeds panic/oops stack printing, scheduler `show_stack()`, wait-channel discovery, and `CONFIG_STACKTRACE` capture.

Important APIs/functions: `arc_unwind_core()` is the iterator used by all consumers. `seed_unwind_frame_info()` seeds `struct unwind_frame_info` from explicit `pt_regs`, current live registers, or a sleeping task saved in `__switch_to`. Public entry points are `show_stacktrace()`, `show_stack()`, `__get_wchan()`, `save_stack_trace_tsk()`, and `save_stack_trace()`.

Control flow: the seed path selects synchronous current-task unwind, asynchronous exception unwind, or sleeping-task unwind. `arc_unwind_core()` repeatedly reads `UNW_PC()`, validates that it is kernel text, invokes a callback, calls `arc_unwind()`, then advances return state from `blink`. Callback variants print symbols, collect stack entries, skip scheduler frames, or stop on the first non-scheduler frame.

State and persistence: no durable state is owned here. It reads task thread saved FP/SP/BLINK, live ARC registers, and caller-provided stack trace buffers. The loop guard stops after 128 frames to avoid unwinder loops.

Dependencies and integration: depends on `CONFIG_ARC_DW2_UNWIND`, `asm/unwind.h`, kallsyms, scheduler helpers, and ARC `switch_to` layout macros. Exported symbols are consumed by kernel diagnostics and generic stacktrace users.

Risks: sleeping-task unwinding assumes the task is not running and that `__switch_to` saved-register layout matches the compensating SP adjustment. Without DWARF unwind support, only a warning is emitted and traces are empty. Bad unwind metadata can truncate or loop until the guard trips.

Test signals: useful checks are panic/oops stack output, `/proc/<pid>/stack`, `__get_wchan()` on sleeping tasks, `CONFIG_STACKTRACE` users, and builds with and without `CONFIG_ARC_DW2_UNWIND`.
