# sources/distributed-fs/ceph-client/arch/riscv/kernel/mcount-dyn.S

Purpose: Provides the dynamic ftrace caller trampoline for RISC-V.

Important APIs/types/functions: Defines `ftrace_caller`, inner labels `ftrace_call` and `ftrace_caller_direct`, and `ftrace_stub_direct_tramp`.

Control flow: Instrumented function calls enter the trampoline, which saves live argument/return state, computes the traced function and parent caller, optionally resolves per-callsite direct ops, calls the active ftrace function, then restores state and returns to the instrumented function.

State and persistence: Uses patched call targets and optional per-record ops state managed by ftrace core; no standalone persistent data beyond trampoline text.

Dependencies and integration points: Integrated with `ftrace.c`, dynamic patching, function graph tracing, direct ftrace, and RISC-V calling convention.

Risks and test signals: Register save masks and stack layout must preserve all call ABI expectations. Test dynamic ftrace, direct ftrace, graph tracing, nested tracers, and module call sites under heavy tracing.
