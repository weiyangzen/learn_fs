# sources/distributed-fs/ceph-client/arch/s390/kernel/mcount.S

Purpose: assembly trampolines for s390 ftrace, function graph tracing, hotpatch branch thunks, and rethook return interception.

Important symbols: `ftrace_stub`, `ftrace_stub_direct_tramp`, `ftrace_regs_caller`, `ftrace_caller`, `ftrace_common`, optional `return_to_handler`, `ftrace_shared_hotpatch_trampoline_br`, optional `ftrace_shared_hotpatch_trampoline_exrl`, and optional `arch_rethook_trampoline`.

Control flow: ftrace caller entries build packed traced-function frames plus `ftrace_regs`/`pt_regs`-compatible data, compute the traced function address from `%r0 - MCOUNT_INSN_SIZE`, load `function_trace_op` and `ftrace_func`, call the active tracer, restore registers, and branch to the selected return address. Function graph support calls `ftrace_return_to_handler()` and returns to its chosen address. Hotpatch trampolines load target registers and branch directly or through expoline `exrl`. Rethook builds full pt_regs, calls `arch_rethook_trampoline_callback()`, then restores PSW/registers through `lpswe`.

Dependencies and integration: depends on generated asm offsets, ftrace ABI, nospec branch macros, expoline config, rethook config, and kprobes text section placement.

Risks and test signals: stack frame layout, PSW preservation, `%r14/%r15` handling, and expoline return paths are critical. Test function tracer with and without full regs, graph tracer, direct trampolines, live ftrace patching, rethook users, and expoline-enabled builds.
