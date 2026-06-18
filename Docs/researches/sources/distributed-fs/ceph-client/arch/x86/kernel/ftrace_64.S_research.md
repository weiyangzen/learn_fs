# sources/distributed-fs/ceph-client/arch/x86/kernel/ftrace_64.S

## Purpose
Implements 64-bit x86 ftrace assembly stubs for dynamic and non-dynamic fentry, regs-aware tracing, graph tracing, direct call handling, return thunks, and IBT/retpoline-safe control transfer.

## Important APIs And Labels
Exports `__fentry__`; defines typed `ftrace_stub`, `ftrace_stub_graph`, `ftrace_caller`, `ftrace_caller_op_ptr`, `ftrace_call`, `ftrace_caller_end`, `ftrace_regs_caller`, `ftrace_regs_caller_op_ptr`, `ftrace_regs_call`, `ftrace_regs_caller_jmp`, `ftrace_regs_caller_end`, `ftrace_stub_direct_tramp`, and `return_to_handler`.

## Control Flow And State
Macros `save_mcount_regs` and `restore_mcount_regs` create the stack and pt_regs-compatible layout expected by C callbacks. Dynamic mode routes `__fentry__` to a cheap return until ftrace patches sites. `ftrace_caller` saves volatile registers, computes `ip` and parent IP, loads `function_trace_op`, supplies a regs pointer, and permits callback-modified RIP. `ftrace_regs_caller` saves full pt_regs state and uses `ORIG_RAX` to encode direct-call behavior. `return_to_handler` builds exit regs, calls `ftrace_return_to_handler()`, then returns via a retpoline/RSB-balanced pattern.

## Dependencies And Integration Points
Coupled with trampoline cloning in `ftrace.c`; label offsets are copied into executable trampolines. Depends on CFI/IBT annotations, call-depth accounting, unwind hints, pt_regs offsets, retpoline alternatives, and function graph tracer core.

## Risks And Test Signals
Risks include breaking trampoline layout, incorrect unwind metadata, missed ENDBR/no-ENDBR annotations, direct-call stack imbalance, and handler-modified RIP corruption. Tests should exercise dynamic ftrace with args, regs and non-regs callbacks, graph tracer, direct trampoline calls, IBT-enabled kernels, retbleed/call-depth mitigations, and objtool checks.
