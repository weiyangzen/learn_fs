# sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind.h

Purpose: public x86 stack unwinder state and helpers for ORC, frame-pointer, and fallback unwinders.

Important APIs/types/functions: `struct unwind_state`, `__unwind_start()`, `unwind_start()`, `unwind_next_frame()`, `unwind_get_return_address()`, `unwind_get_return_address_ptr()`, `unwind_done()`, `unwind_error()`, `unwind_get_entry_regs()`, `unwind_init()`, `unwind_module_init()`, `unwind_recover_rethook()`, `unwind_recover_ret_addr()`, `READ_ONCE_TASK_STACK()`, and `task_on_another_cpu()`.

Control flow: callers initialize with task/regs/first frame, then iterate `unwind_next_frame()` until `STACK_TYPE_UNKNOWN`. ORC and frame-pointer builds store different cursor fields. Return-address recovery first accounts for ftrace graph rewriting, then rethook trampoline rewriting. Entry-reg access exposes full or partial interrupt/exception frames depending on unwinder state.

State/persistence: unwind cursor state is per-call stack data. Persistent inputs include task stacks, ORC metadata, module ORC tables, ftrace graph state, and rethook lists.

Dependencies/integration: depends on scheduler tasks, ftrace, rethook, ptrace, stacktrace, module metadata, and KASAN-safe stack reads. Integrated with stack traces, livepatch/debugging, lockdep, oops reporting, perf, and BPF stack walkers.

Risks/test signals: unwinding across interrupts, rethooks, ftrace, modules, and remote running tasks is fragile. Test ORC and frame-pointer configs, module load/unload with ORC data, ftrace graph tracer, kretprobe/rethook users, NMI/oops stack traces, and KASAN remote stack-read behavior.
