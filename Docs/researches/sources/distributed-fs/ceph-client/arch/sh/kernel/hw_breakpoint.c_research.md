# sources/distributed-fs/ceph-client/arch/sh/kernel/hw_breakpoint.c

Purpose: adapts the SuperH UBC hardware breakpoint unit to Linux perf/hw_breakpoint and ptrace.

Important APIs and control flow: per-CPU `bp_per_reg[]` tracks perf events assigned to UBC channels. `arch_install_hw_breakpoint()` finds a free channel, enables the UBC clock, and programs hardware via `sh_ubc->enable()`. `arch_uninstall_hw_breakpoint()` disables the channel and clock. `hw_breakpoint_arch_parse()` maps generic length/type to SH encodings and enforces alignment. `hw_breakpoint_handler()` reads triggered channel masks, disables channels, calls `perf_bp_event()`, sends user `SIGTRAP` for user breakpoints, clears trigger bits, and re-enables active channels except ptrace one-shot events. `register_sh_ubc()` installs the platform UBC implementation.

State, dependencies, and risks: state includes global `sh_ubc`, per-CPU channel event arrays, UBC clock state, and ptrace breakpoints in task thread state. Dependencies include perf event core, die notifier trap flow, kprobes-safe handlers, `ptrace_triggered`, and platform UBC ops. Risks include channel exhaustion, clock imbalance, incorrect triggered masks, and ptrace one-shot semantics conflicting with perf watchpoints. Test signals are perf watchpoints, ptrace single-step/watchpoint, concurrent CPU breakpoints, and UBC registration on supported CPUs.
