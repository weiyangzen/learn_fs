<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace_dyn.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace_dyn.c

Purpose: implements dynamic ftrace text patching for LoongArch.
Important APIs and types: provides `ftrace_make_call`, `ftrace_make_nop`, `ftrace_update_ftrace_func`, and helpers to generate branch/NOP sequences and validate patched instructions.
Control flow: ftrace core asks the arch code to replace callsite instructions with calls to ftrace trampoline or NOPs; patching uses LoongArch instruction helpers and cache flushes.
State and persistence: modifies kernel/module text while tracing is enabled or disabled.
Dependencies and integration: depends on `inst.c`, ftrace core, module relocation sections, stop_machine/text patching, and instruction cache coherency.
Risks and test signals: branch range or patch atomicity failures can crash executing CPUs. Signals include dynamic ftrace selftests, module ftrace, graph tracer, concurrent enable/disable, and objdump checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/ftrace_dyn.c -->
