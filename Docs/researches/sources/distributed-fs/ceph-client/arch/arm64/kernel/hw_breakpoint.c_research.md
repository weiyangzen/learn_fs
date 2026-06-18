# sources/distributed-fs/ceph-client/arch/arm64/kernel/hw_breakpoint.c

Purpose: Implements arm64 hardware breakpoint/watchpoint support for perf, ptrace, kernel debugging, CPU suspend restore, and exception handling.

Important APIs and state: per-CPU `bp_on_reg[]`, `wp_on_reg[]`, and `stepping_kernel_bp` track register ownership and single-step state. Global `core_num_brps` / `core_num_wrps` cache register counts. Entry points include `hw_breakpoint_slots()`, `arch_install_hw_breakpoint()`, `arch_uninstall_hw_breakpoint()`, `hw_breakpoint_arch_parse()`, `arch_bp_generic_fields()`, `do_breakpoint()`, `do_watchpoint()`, `try_step_suspended_breakpoints()`, `hw_breakpoint_thread_switch()`, and `hw_breakpoint_reset()`.

Control flow: install/uninstall allocates a slot, enables/disables debug monitors for EL0 or EL1, writes address and control registers, and respects per-task disabled flags. Attribute parsing maps generic perf breakpoint types and lengths into arch encodings, aligns addresses, handles compat tasks, and rejects per-task kernel breakpoints. Exception handlers match trigger addresses, report perf events, disable matching registers, and single-step past the trapped instruction before restoring the registers.

Dependencies and integration: uses debug monitor sysregs, perf breakpoint core, task `debug_info`, ptrace compat state, CPU hotplug, CPU suspend debug restorer hooks, and kprobes restrictions (`NOKPROBE_SYMBOL`).

Risks and test signals: risks are slot leaks, stale per-CPU register programming after CPU PM, imprecise watchpoint address attribution, nested single-step conflicts, compat alignment mistakes, and kernel/user privilege confusion. Test with perf breakpoints/watchpoints, ptrace hardware debug, CPU hotplug/suspend, compat AArch32 watchpoints, overlapping watchpoints, and kernel breakpoint stepping.
