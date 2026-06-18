<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/switch.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/switch.c

## Purpose
`switch.c` implements nVHE guest entry/exit. It saves host state, restores guest state, switches stage-2 context, enables traps/timers/VGIC/debug/PMU state, loops through handled guest exits, then restores host state and handles hyp panic cleanup.

## Important APIs, Types, and Functions
Per-CPU `kvm_host_data`, `kvm_hyp_ctxt`, and `kvm_hyp_vector` store host context and selected vectors. `__activate_traps()` and `__deactivate_traps()` program HCR/MDCR/CPTR/VBAR and speculative-AT workaround state. `__hyp_vgic_save_state()` / `__hyp_vgic_restore_state()` handle GICv3/v5 CPU interfaces. `hyp_exit_handlers[]` and `pvm_exit_handlers[]` map ESR exception classes to handlers. `fixup_guest_exit()` enforces protected-VM AArch64-only state and calls common exit fixups. `__kvm_vcpu_run()` is the main guest-run function. `hyp_panic()` restores host context enough to report a panic.

## Control Flow, State, and Persistence
Guest run sets `host_ctxt->__hyp_running_vcpu`, switches PMU counters, saves host sysregs and debug buffers, restores guest sysregs/stage-2/traps/VGIC/timer/debug state, enters the guest via `__guest_enter()`, and repeats while exits are handled in hyp. On final exit it saves guest state, disables traps, reloads host stage-2/sysregs/debug/PMU state, clears the running vCPU, and returns the exit code. Protected VMs use stricter handler tables that handle HVC/sysregs in hyp or inject undefined exceptions.

## Dependencies and Integration Points
It depends on generic hyp switch/sysreg/debug/VGIC/timer helpers, protected sysreg/HVC handlers in `sys_regs.c` and `pkvm.c`, TLB/stage-2 loading, host context assembly, tracing, and stacktrace panic support.

## Risks and Test Signals
Risks include ordering bugs around stage-1/stage-2 switches, failing to restore host debug/SPE/PMU state, pVM exit misclassification, 32-bit protected guest escape, and IRQ priority masking mistakes. Test signals are guest boot and exit storms, protected VM restricted sysreg/HVC handling, PMU/debug/SPE save-restore tests, GICv3/v5 paths, timer trap behavior, panic cleanup while a vCPU is active, and speculative-AT workaround configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/switch.c -->
