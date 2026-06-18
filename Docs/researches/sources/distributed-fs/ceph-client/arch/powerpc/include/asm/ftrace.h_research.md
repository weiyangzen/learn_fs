# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ftrace.h

Purpose: Supplies PowerPC-specific ftrace constants, register accessors, syscall-name matching, graph tracing hooks, per-CPU ftrace enable state, and trampoline metadata.

Important APIs, types, and functions: Defines `MCOUNT_ADDR`, `MCOUNT_INSN_SIZE`, `FTRACE_MCOUNT_MAX_OFFSET`, `struct dyn_arch_ftrace`, `arch_ftrace_get_regs()`, `arch_ftrace_fill_perf_regs()`, ftrace register getters/setters, `ftrace_graph_func()`, `arch_syscall_match_sym_name()`, `this_cpu_*_ftrace()` helpers, trampoline symbols, `ftrace_free_init_tramp()`, `ftrace_call_adjust()`, and direct-call support through `arch_ftrace_set_direct_caller()`.

Control flow: Dynamic ftrace patches call sites or patchable entries, initializes NOPs, optionally routes through out-of-line stubs, snapshots register state for callbacks/perf, and uses per-CPU PACA state to gate tracing on PPC64.

State and persistence: Runtime state includes per-callsite metadata, optional out-of-line stub pointers, PACA `ftrace_enabled`, and trampoline text ranges. It is kernel-memory state only.

Dependencies and integration points: Depends on ftrace core, `linux/ftrace_regs.h`, module metadata, PACA on PPC64, and PowerPC text patching/trampoline code.

Risks: Call-site offsets and ABI register fields must match compiler output. Syscall symbol matching has PowerPC-specific prefixes. Direct-call and graph paths modify return IP/link fields, so bad register handling can corrupt returns. Init trampoline lifetime must match module/core patching.

Test signals: Build/function tracing with `CONFIG_FUNCTION_TRACER`, dynamic ftrace with args/regs/direct calls, syscall tracing for `ppc_`, `ppc32_`, and `ppc64_` names, graph tracing, module tracepoints, and per-CPU enable/disable behavior.
