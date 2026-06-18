# sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace_32.S

## Purpose
Implements 32-bit x86 ftrace assembly entry stubs for fentry/mcount callbacks, regs callbacks, direct trampolines, and function graph return redirection.

## Important APIs And Labels
Exports `__fentry__`; defines `ftrace_caller`, `ftrace_call`, `ftrace_graph_call`, weak `ftrace_stub`, `ftrace_regs_caller`, `ftrace_regs_call`, `ftrace_stub_direct_tramp`, `ftrace_graph_caller`, and `return_to_handler`.

## Control Flow And State
`ftrace_caller` preserves the minimal caller-saved register set, fabricates frame-pointer state when needed, computes traced IP as return address minus `MCOUNT_INSN_SIZE`, loads parent IP and `function_trace_op`, and calls the patched target at `ftrace_call`. `ftrace_regs_caller` builds a pt_regs-like frame, passes it as the fourth argument, permits callback-modified IP/EAX restoration, and returns through the normal stub path. Graph caller invokes `prepare_ftrace_return()`, and `return_to_handler` calls `ftrace_return_to_handler()` then jumps indirectly to the restored return target.

## Dependencies And Integration Points
Tightly coupled to `ftrace.c`, x86 calling conventions, `asm-offsets.h` pt_regs offsets, frame-pointer configuration, retpoline macros, and function graph tracer core.

## Risks And Test Signals
Risks include stack layout drift, wrong frame-pointer emulation, register clobbering, incorrect parent IP extraction, and unsafe indirect return. Test signals are successful 32-bit ftrace callbacks with and without frame pointers, regs callbacks, graph tracing, direct trampolines, and objtool/unwind validation.
