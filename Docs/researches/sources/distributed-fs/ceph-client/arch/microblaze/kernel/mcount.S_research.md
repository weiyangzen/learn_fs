# sources/distributed-fs/ceph-client/arch/microblaze/kernel/mcount.S

Purpose: supplies the assembly `_mcount` trampoline and optional function graph return trampoline used by MicroBlaze ftrace.

Important symbols and state: exports `ftrace_stub`, `_mcount`, `ftrace_caller`, `ftrace_call_graph`, `ftrace_call`, and `return_to_handler`. Macros save/restore most GPRs in a 120-byte frame.

Control flow: `_mcount` optionally jumps over disabled dynamic ftrace, saves registers and original link register, handles function-graph return replacement through `prepare_ftrace_return()`, then calls the current trace function via `r20`. `return_to_handler` calls `ftrace_return_to_handler()` and returns to the address it supplies.

State and persistence: no static storage here; it consumes global ftrace function pointers and mutates stack frames.

Dependencies and integration: dynamic patch sites are modified by `ftrace.c`; module exports are provided through `microblaze_ksyms.c`.

Risks and test signals: save-frame offsets must match ftrace.c expectations for parent/current addresses. Test static and dynamic ftrace, graph tracing, nested tracing, and builds with tracer disabled.
