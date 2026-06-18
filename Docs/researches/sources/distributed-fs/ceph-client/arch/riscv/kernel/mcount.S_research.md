# sources/distributed-fs/ceph-client/arch/riscv/kernel/mcount.S

Purpose: Implements classic RISC-V mcount/ftrace entry stubs and graph return handler.

Important APIs/types/functions: Defines `ftrace_stub`, `ftrace_stub_graph`, `return_to_handler`, and `_mcount`.

Control flow: Compiler-instrumented functions call `_mcount`, which saves registers, invokes ftrace and optional graph tracer hooks, then restores execution. `return_to_handler` redirects function returns through graph tracing and resumes at the original return address.

State and persistence: Uses ftrace core global function pointers and per-task graph return state. Assembly text is persistent.

Dependencies and integration points: Works with `ftrace.c`, function graph tracer, compiler `-pg` instrumentation, and RISC-V ABI.

Risks and test signals: Incorrect frame layout or return address handling corrupts call chains. Test function tracer and graph tracer in static and dynamic ftrace modes, recursion handling, and interrupt-context tracing.
