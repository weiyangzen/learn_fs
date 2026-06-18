# sources/distributed-fs/ceph-client/arch/sh/lib/mcount.S

Purpose: implements SH ftrace/mcount entry stubs, dynamic call sites, and function-graph tracing return handling.

Important symbols: `_mcount`, `mcount`, `mcount_call`, `ftrace_caller`, `ftrace_call`, `ftrace_stub`, `ftrace_graph_caller`, `return_to_handler`, and graph return/entry labels.

Control flow: compiler-inserted mcount calls enter lightweight assembly, save enough state, dispatch to the configured ftrace callback or graph tracer, and restore execution. Graph tracing rewrites return addresses and uses `return_to_handler` to resume through ftrace's return hook.

State and persistence: manipulates stack frames, return addresses, and ftrace callback patch sites. Runtime state is controlled by generic ftrace infrastructure.

Dependencies and integration: depends on `asm/ftrace.h`, thread info offsets, panic/dump-stack fallbacks, and dynamic ftrace patching.

Risks: stack/register preservation errors crash arbitrary instrumented functions. Graph return rewriting is especially sensitive to frame layout and interrupt context.

Test signals: ftrace function and function-graph tracer tests, dynamic enable/disable, recursion tests, and panic path validation.
