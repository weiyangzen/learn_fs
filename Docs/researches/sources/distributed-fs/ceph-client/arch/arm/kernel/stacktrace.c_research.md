# sources/distributed-fs/ceph-client/arch/arm/kernel/stacktrace.c

Purpose: implements ARM stack frame unwinding and generic stack trace walking for current, saved, and register-based contexts.

Important APIs/types/functions: `unwind_frame`, `walk_stackframe`, and `arch_stack_walk`. Internal `frame_pointer_check` validates frame-pointer bounds and handles stack switches through `call_with_stack`.

Control flow: frame-pointer unwinding validates FP/SP boundaries, handles exception frames by returning saved PC from `pt_regs`, restores FP/SP/PC according to GCC or Clang prologue layout, resolves kretprobe trampolines, and marks entry text as exception frames. `arch_stack_walk` seeds frames from regs, current task, or non-current uniprocessor saved context, then invokes the consumer callback.

State and persistence: no persistent state; stackframe structure carries transient unwind state and optional kretprobe cursor.

Dependencies and integration: used by stacktrace core, perf, oops dumps, `process.c`, kprobes/kretprobes, and exception entry text markers.

Risks: unwinding arbitrary stacks is fragile, especially non-current SMP tasks; false exception frames can access invalid stack data; compiler prologue differences matter. Test signals include stacktrace selftests, oops backtraces, kretprobe traces, IRQ stack traces, and Clang/GCC builds.
