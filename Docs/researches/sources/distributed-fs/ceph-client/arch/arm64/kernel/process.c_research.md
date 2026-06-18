# sources/distributed-fs/ceph-client/arch/arm64/kernel/process.c

Purpose: this file implements ARM64 process and CPU lifecycle glue: reboot/halt/poweroff, register dumping, thread flush/duplication, fork setup, context switching, stack alignment, new-exec architecture setup, tagged-address/MTE controls, and PR_TSC controls.

Important APIs and state: exported state includes `pm_power_off`, optional `__stack_chk_guard`, and per-CPU `__entry_task`. System lifecycle functions include `machine_shutdown()`, `machine_halt()`, `machine_power_off()`, and `machine_restart()`. Task lifecycle functions include `flush_thread()`, `arch_dup_task_struct()`, `arch_release_task_struct()`, `copy_thread()`, `tls_preserve_current_state()`, and `__switch_to()`. User ABI helpers include `set_tagged_addr_ctrl()`, `get_tagged_addr_ctrl()`, `get_tsc_mode()`, `set_tsc_mode()`, and `arch_elf_adjust_prot()`.

Control flow: fork copies current pt_regs for user tasks or synthesizes kernel-thread regs, initializes kernel PAC keys, snapshots TLS/POE state, handles CLONE_SETTLS, conditionally inherits SME ZA/TPIDR2 for fork but not CLONE_VM threads, allocates GCS stack state, and sets the CPU context to `ret_from_fork`. Context switching is ordered: debug state check, FPSIMD, TLS, breakpoints, context ID, entry task, SSBS, counter access, pointer auth, POE, GCS, full `dsb(ish)`, MTE, user SCTLR update, MPAM, then `cpu_switch_to()`.

State and persistence: per-task architecture state lives under `thread_struct`: TLS, FP/SVE/SME storage, PAC keys and `sctlr_user`, POE `por_el0`, GCS metadata, breakpoint state, MTE flags, and TSC trapping flags. `flush_thread()` resets user-exposed state on exec. The tagged-address sysctl `abi.tagged_addr_disabled` only blocks future opt-in.

Dependencies and integration: integrates with scheduler, reboot, EFI, SMP, FPSIMD/SVE/SME, PAC, GCS, MTE, MPAM, hw breakpoints, compat mode, ELF loader, prctl, sysctl, and timer errata. `pointer_auth.c`, `ptrace.c`, and `signal.c` rely on these helpers for state synchronization.

Risks: context-switch order is correctness-critical for speculation mitigations, lazy FP state, MTE asynchronous faults, and PAC SCTLR updates. Fork handling must avoid sharing stale SVE/SME buffers. Tagged-address and TSC controls are ABI-visible and must reject compat tasks where unsupported.

Test signals: fork/clone/exec tests across native and compat tasks, MTE/tagged address prctl tests, PAC/GCS/SME context-switch tests, CPU hotplug and kexec/reboot paths, and ptrace mutation of FP/TLS state.
