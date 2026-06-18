## sources/distributed-fs/ceph-client/arch/arm64/include/asm/ftrace.h

Purpose: arm64 ftrace, function graph tracing, direct-call, syscall-trace, and ftrace-regs ABI definitions.

Important APIs/types/functions: defines ftrace instruction sizes, PLT counts, stack tracer shift, `struct dyn_arch_ftrace`, `struct __arch_ftrace_regs`, ftrace regs accessors, partial pt_regs conversion, perf regs fill macro, `ftrace_call_adjust`, `arch_ftrace_get_symaddr`, `ftrace_init_nop`, `ftrace_graph_func`, direct caller setter, syscall compat ignore hooks, syscall symbol matching, and `prepare_ftrace_return`.

Control flow: dynamic ftrace patches callsites to branch to trampolines; trampolines capture selected registers, optionally redirect returns, and feed graph/perf/syscall tracing.

State and persistence: ftrace callsites and graph call targets are patched in kernel text; `ftrace_regs` captures transient call state.

Dependencies and integration: depends on instruction encoding, dynamic ftrace, function graph tracer, perf, syscall tracing, compat detection, and module text patching.

Risks: wrong register layout or instruction adjustment corrupts traced functions or stack unwinding. Test signals are ftrace selftests, function graph tracer, direct-call tests, perf callchains, module tracing, and compat syscall trace filtering.
