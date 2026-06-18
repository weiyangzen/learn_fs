<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/stacktrace.c

Purpose: Implements RISC-V kernel and user stack walking, stack display, wait-channel lookup, and user-stack unwinding callbacks.

Important APIs/types/functions: Provides `walk_stackframe()`, `show_stack()`, `get_wchan()` support via `save_wchan()`, `unwind_user_frame()`, and `arch_stack_walk_user()`.

Control flow: Kernel walking starts from pt_regs, current frame pointer, or blocked task frame state, validates each frame pointer against stack bounds, consumes return addresses, and stops on invalid frames or callback termination. User walking validates user frame records with `access_ok()` and copies frame/return PCs from user memory.

State and persistence: No persistent state; it reads task stacks, pt_regs, and frame records. It treats exception-entry ranges specially to avoid reporting internal trampoline PCs.

Dependencies and integration points: Used by `return_address.c`, stack dumps, perf/ftrace-style walkers, scheduler wait-channel reporting, and user stack unwinding.

Risks: Frame-pointer assumptions make unwinding unreliable without proper compiler options. Bad stack validation can read outside task stacks or loop forever; user unwind must handle faults gracefully.

Test signals: Kernel backtraces through normal, interrupt, and exception contexts; blocked-task `wchan`; user stack walking with valid and invalid frame chains; and ORC/fp config variants.

Source read size: 226 lines, 5474 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/stacktrace.c -->
