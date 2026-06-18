
# sources/distributed-fs/ceph-client/arch/x86/include/asm/debugreg.h

Purpose: x86 debug-register access, breakpoint save/restore, AMD address-mask hooks, and debug-control MSR helpers.

Important APIs and control flow: `native_get_debugreg()` and `native_set_debugreg()` switch on DR0-DR3, DR6, and DR7; DR7 access is volatile to avoid unsafe reordering under SEV-ES #VC handling. `hw_breakpoint_disable()` resets DR7 and address registers. `local_db_save()` skips hypervisor cases without active breakpoints, disables DR7 when nonzero, and returns the old value; `local_db_restore()` restores after a compiler barrier. Optional AMD mask hooks and `get/update_debugctlmsr()` wrap debug-control MSR access.

State, dependencies, and risks: state includes hardware debug registers, per-CPU `cpu_dr7`, AMD debug masks, and DEBUGCTL MSR. Dependencies include uapi debugreg bits, cpufeatures, MSRs, paravirt overrides, and breakpoint core. Risks include unsafe DR7 access in entry/NMI contexts, losing breakpoints around critical sections, and SEV-ES reordering. Test signals are hw_breakpoint selftests, perf debug events, SEV-ES boot, and ptrace debug register tests.
