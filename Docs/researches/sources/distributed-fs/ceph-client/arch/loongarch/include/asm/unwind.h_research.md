<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind.h

Purpose: defines LoongArch unwinder state and interfaces for kernel stack walking.
Important APIs and types: declares `struct unwind_state`, `unwind_start`, `unwind_next_frame`, `unwind_get_return_address`, `unwind_done`, and default frame handling helpers.
Control flow: stacktrace and debugging code initialize state from task/regs, repeatedly call `unwind_next_frame`, and consume return addresses until `unwind_done`.
State and persistence: unwinder state is transient and tracks stack pointer, frame pointer, program counter, task, and reliability flags during a walk.
Dependencies and integration: used by `stacktrace.c`, `unwind_guess.c`, ftrace, livepatch, panic backtraces, and objtool/unwind hints.
Risks and test signals: invalid frame validation can read outside stacks or hide unreliable traces. Signals include stacktrace tests, panic backtraces, reliable-stack livepatch checks, and ftrace recursion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind.h -->
