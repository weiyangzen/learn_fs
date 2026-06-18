# sources/distributed-fs/ceph-client/arch/x86/kernel/hw_breakpoint.c

## Purpose
Implements x86 perf hardware breakpoints using debug registers DR0-DR7, including validation, install/uninstall, ptrace cleanup, KVM restore support, and #DB notifier handling.

## Important APIs, Types, And State
Exports per-CPU `cpu_dr7`, `encode_dr7()`, `decode_dr7()`, `arch_install_hw_breakpoint()`, `arch_uninstall_hw_breakpoint()`, `arch_bp_generic_fields()`, `arch_check_bp_in_kernelspace()`, `hw_breakpoint_arch_parse()`, `flush_ptrace_hw_breakpoint()`, `hw_breakpoint_restore()`, `hw_breakpoint_exceptions_notify()`, and stub `hw_breakpoint_pmu_read()`. Per-CPU state tracks debug address registers in `cpu_debugreg[]` and occupying perf events in `bp_per_reg[]`.

## Control Flow
Parsing validates address range, excludes CPU entry/GDT/TSS/TLB/debug-register-sensitive ranges, enforces kprobe blacklist for kernel execute breakpoints, maps generic breakpoint types/lengths to x86 encodings, supports AMD range masks, and checks alignment. Installation finds a free DR slot with IRQs disabled, writes DRn, updates cached DR7 before hardware DR7, and applies AMD address masks. Uninstall clears the slot, writes hardware DR7 before cache, and clears masks. #DB notifier reads DR6, dispatches matching perf breakpoint events, clears handled trap bits, sets RF for execute breakpoints, and leaves user or multi-cause debug exceptions to generic debug handling.

## Dependencies And Integration Points
Integrates with perf events, ptrace debug registers, kprobes blacklist, KVM debug-register restore, die notifier `DIE_DEBUG`, CPU entry area definitions, AMD BPEXT masks, and x86 debug register helpers.

## Risks And Test Signals
Risks include debug-register cache/hardware ordering during NMIs, breakpoints on entry-critical memory causing recursive #DB, incorrect DR6 cause handling, AMD range mask validation, and ptrace/perf slot conflicts. Tests include perf user/kernel breakpoints, ptrace DR use, KVM guest switching, NMI-heavy scenarios, kprobe blacklisted addresses, CPU hotplug/restore, AMD range breakpoints, and alignment/error return cases.
