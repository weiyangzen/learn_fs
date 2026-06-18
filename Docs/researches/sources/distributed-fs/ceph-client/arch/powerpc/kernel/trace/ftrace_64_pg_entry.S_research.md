# sources/distributed-fs/ceph-client/arch/powerpc/kernel/trace/ftrace_64_pg_entry.S

## Purpose
Provides PPC64 legacy profiling ftrace assembly entry points for `ftrace_caller`, `_mcount`, graph caller stubs, return handler, and reserved trampolines.

## Important APIs, Types, and Functions
- `ftrace_caller` checks `PACA_FTRACE_ENABLED`, saves LR/stack state, computes traced IP and parent IP, calls patched `ftrace_call`, optionally branches to graph caller, and restores state.
- `ftrace_stub` and `ftrace_graph_stub` are no-op branch targets.
- `ftrace_graph_caller` calls `prepare_ftrace_return()` and rewrites caller LR in the stack frame.
- `_mcount`/`mcount` return through LR/CTR and export `_mcount`.
- `return_to_handler` saves return values/TOC, calls `ftrace_return_to_handler`, and returns to the real address.
- `ftrace_tramp_text` and `ftrace_tramp_init` reserve trampoline storage.

## Control Flow and State
An instrumented function branches here before its normal body has fully executed. The caller saves enough state to call C tracing code while preserving ABI TOC and LR semantics, then restores stack and LR. Function graph tracing diverts the saved return address to `return_to_handler`.

## State and Persistence Behavior
Uses stack frames and PACA ftrace enable state. Trampolines are patched by `ftrace_64_pg.c`.

## Dependencies and Integration Points
Coupled to `ftrace_64_pg.c` patch targets, PPC64 TOC ABI, `prepare_ftrace_return()`, `ftrace_return_to_handler`, PACA layout, and module TOC switching.

## Risks
Incorrect stack offsets or TOC restoration corrupts traced functions. Graph return rewriting must identify the caller frame correctly. Trampoline storage must be sized for generated stubs.

## Test Signals
Legacy PPC64 ftrace, graph tracing, module tracing, nested traced calls, tracing disabled/enabled per CPU, and return-value preservation tests.
