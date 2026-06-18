<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stacktrace.h

Purpose: declares Xtensa stack-walking primitives and a minimal `struct stackframe` with `pc` and `sp`. Important APIs are `stack_pointer`, `walk_stackframe`, `xtensa_backtrace_kernel`, and `xtensa_backtrace_user`.

Control flow is implemented in `kernel/stacktrace.c`: callers seed a stack pointer or pt_regs, and callback-driven walkers report frames. State is task stack content and saved thread stack pointer. Dependencies include scheduler/task structures and Xtensa return-address encoding. Integration points are perf callchains, `return_address`, oops stack dumps, tracing, and scheduler diagnostics. Risks are invalid SP boundaries, register-window ABI return-address reconstruction, user memory faults while walking user stacks, and stale `thread.sp` for running tasks. Test signals include perf callchains, oops stack output, `save_stack_trace`, sleeping task `wchan`, and user/kernel backtrace tests for both ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stacktrace.h -->
