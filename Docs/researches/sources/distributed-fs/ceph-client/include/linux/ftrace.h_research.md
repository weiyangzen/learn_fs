<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace.h -->
# sources/distributed-fs/ceph-client/include/linux/ftrace.h

Purpose: Provides the main Linux function tracing API, including runtime function callbacks, dynamic call-site patching, module symbol lookup, register access, direct-call support, stack tracing coordination, and function graph tracing interfaces.

Important APIs/types/functions: Key types include `ftrace_ops`, `ftrace_regs`, `dyn_ftrace`, `ftrace_ops_hash`, `ftrace_func_entry`, `ftrace_graph_ent`, `ftrace_graph_ret`, `fgraph_ops`, and `ftrace_ret_stack`. Important functions include `register_ftrace_function()`, `unregister_ftrace_function()`, `ftrace_ops_get_func()`, dynamic filter setters, direct-call registration/modification, `ftrace_make_nop()`, `ftrace_make_call()`, `ftrace_modify_call()`, module init/enable/release helpers, graph tracer registration, and `ftrace_kill()`. Numerous flags (`FTRACE_OPS_FL_*`, `FTRACE_FL_*`) describe callback capabilities and call-site state.

Control flow: Function entry instrumentation reaches architecture ftrace callers, which dispatch through either a unique ops callback or an ops list depending on architecture support. Dynamic ftrace records describe mcount/fentry sites; filters select records; update functions decide whether to make calls, nops, or modify call targets; architecture hooks patch text under safe synchronization. Function graph tracing replaces return addresses and later dispatches return handlers.

State and persistence behavior: Runtime state includes global `ftrace_enabled`, the RCU-linked `ftrace_ops_list`, dynamic hashes, per-record flags/counters, trampoline addresses, per-task graph return stacks, static keys, and tracing buffers. No state is persistent across boot except build-time instrumentation sections.

Dependencies and integration points: Depends on architecture ftrace support, kallsyms, modules, static keys, tracing buffers, pt_regs/ftrace_regs accessors, stack tracer state, preempt tracing, syscall tracing, and text patching infrastructure. It is a cross-cutting integration point for tracing, live patching, BPF-like direct hooks, perf stack capture, and diagnostics.

Risks: Text patching is architecture-sensitive and must verify expected bytes. `IPMODIFY`, direct calls, save-regs, and graph tracing have exclusivity constraints. Registered `ftrace_ops` must remain allocated after unregister long enough for CPU synchronization. Recursion and RCU flags must match callback behavior. Disabled config paths often return success macros, so build coverage matters.

Test signals: Build matrix over function tracer, dynamic ftrace, regs, direct calls, call ops, graph tracer, modules, and tracing disabled. Run ftrace selftests, filter/notrace writes, module load/unload tracing, direct-call conflict tests with IP modification, stack tracer disable/enable assertions, and graph tracer task lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ftrace.h -->
