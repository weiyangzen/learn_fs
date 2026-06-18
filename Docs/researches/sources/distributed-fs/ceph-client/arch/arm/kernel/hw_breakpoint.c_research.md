# sources/distributed-fs/ceph-client/arch/arm/kernel/hw_breakpoint.c

Purpose: implements ARM hardware breakpoint/watchpoint support for perf, ptrace, debug exceptions, and optional CFI traps by programming CP14 debug registers. It discovers debug architecture level, BRP/WRP counts, monitor-mode availability, OS save/restore support, and maximum watchpoint length.

Important APIs/types/functions: exported architecture hooks include `hw_breakpoint_slots`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `arch_check_bp_in_kernelspace`, `arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `arch_get_debug_arch`, `arch_get_max_wp_len`, `hw_breakpoint_pmu_read`, and `hw_breakpoint_exceptions_notify`. Internal control is built around `read_wb_reg`, `write_wb_reg`, `encode_ctrl_reg`/`decode_ctrl_reg`, `watchpoint_handler`, `breakpoint_handler`, and `hw_breakpoint_pending`.

Control flow: `arch_hw_breakpoint_init` probes CPUID/DIDR, blacklists Scorpion CPUs, registers CPU hotplug reset, clears debug control/value registers, calculates capacities, installs fault hooks, and registers PM restore. Runtime debug aborts enter `hw_breakpoint_pending`, decode DSCR MOE, dispatch to breakpoint/watchpoint/CFI handlers, fire `perf_bp_event`, and use mismatch breakpoints for single-step restoration when the default overflow handler is active.

State and persistence: per-CPU `bp_on_reg[]` and `wp_on_reg[]` track installed perf events. `core_num_brps`, `core_num_wrps`, `debug_arch`, `has_ossr`, and `max_watchpoint_len` are init-time global capability state. CPU PM exit and hotplug reset hardware registers because debug state can be lost across low-power modes.

Dependencies and integration: depends on perf hw breakpoint core, undef hooks, fault-code hooks, CPU hotplug, CPU PM, CoreSight OS lock registers, ARM CP15/CP14 helpers, and optional CFI reporting. Ptrace consumes its generic-field conversions and resource info.

Risks: debug-register access can undef on broken firmware or powered-down debug blocks; alignment and watchpoint attribution are architecture-sensitive; older debug architectures only expose one reliable watchpoint; single-step support requires reserved mismatch BRPs and target-bound events. Test signals include boot logs reporting BRP/WRP counts, max watchpoint size, ptrace/perf breakpoint tests, watchpoint uaccess cases, CPU hotplug/PM resume tests, and unsupported CPU fallback.
