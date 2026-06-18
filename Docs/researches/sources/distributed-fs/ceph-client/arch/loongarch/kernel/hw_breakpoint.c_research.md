<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/hw_breakpoint.c

Purpose: implements LoongArch hardware breakpoint/watchpoint support for perf, ptrace, and KGDB.
Important APIs and types: defines per-CPU breakpoint/watchpoint slot arrays, `hw_breakpoint_slots`, CSR read/write switch helpers, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `arch_check_bp_in_kernelspace`, `arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `breakpoint_handler`, `watchpoint_handler`, `hw_breakpoint_thread_switch`, and `flush_ptrace_hw_breakpoint`.
Control flow: perf events are parsed into arch breakpoint descriptors, assigned to per-CPU slots, written to FWP/MWP CSR register groups, and enabled via CRMD/PRMD bits. Exception handlers scan pending status bits, emit `perf_bp_event`, clear status, and disable or restore breakpoint registers around traps/thread switches.
State and persistence: per-CPU slot arrays track installed perf events; thread fields track ptrace break/watch events; hardware CSR watch registers hold address/mask/control/ASID state.
Dependencies and integration: depends on `asm/hw_breakpoint.h`, perf/hw_breakpoint core, ptrace thread state, kprobes `NOKPROBE`, CPU probe watch counts, CSR helpers, and KGDB hardware breakpoint callbacks.
Risks and test signals: slot accounting, privilege bits, and single-step interactions are fragile. Signals include perf hardware breakpoint tests, ptrace watchpoints, KGDB hardware breakpoints, CPU hotplug, and kprobe recursion safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/hw_breakpoint.c -->
