## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/smp.c

### Purpose
`smp.c` implements PowerNV SMP operations: starting CPUs through OPAL, CPU hotplug/offline loops, IPI routing through doorbells or interrupt controllers, NMI IPI delivery, and registration of PowerNV `smp_ops`.

### Important APIs, Types, And Functions
Key functions are `pnv_smp_setup_cpu()`, `pnv_smp_kick_cpu()`, hotplug helpers `pnv_smp_cpu_disable()`, `pnv_cpu_offline_self()`, `pnv_flush_interrupts()`, `pnv_cpu_bootable()`, `pnv_smp_probe()`, `pnv_cause_ipi()`, `pnv_system_reset_exception()`, `pnv_cause_nmi_ipi()`, and `pnv_smp_init()`.

### Control Flow
Secondary start asks OPAL about the hardware CPU state, starts inactive threads at `generic_secondary_smp_init`, and then kicks the PACA path. Per-CPU setup enables a POWER9 HMI workaround and configures XIVE or XICS. Hotplug marks the CPU offline, migrates interrupt state, enters a loop with hard IRQs disabled, naps through `pnv_cpu_offline()`, handles wake reasons, and exits when restart is requested or crash IPIs arrive. Probe patches `smp_ops->cause_ipi` to doorbell implementations when supported.

### State, Persistence, And Dependencies
State lives in `smp_ops`, PACA fields, `boot_cpuid`, systemcfg processor counts, interrupt-controller state, and CPU online/dead masks. Dependencies include OPAL CPU status/start calls, XIVE/XICS, doorbells, cpuidle, KVM host IPI state, kdump, and subcore split checks.

### Integration Points
The file is called from PowerNV setup and generic CPU hotplug/SMP code. NMI IPI support plugs into `ppc_md.system_reset_exception`.

### Risks
CPU state races with OPAL, kexec, and hotplug can strand CPUs. Offline loops must clear wakeup interrupts correctly and preserve crash dump behavior. Doorbell fallback must remain valid on older cores.

### Test Signals
CPU online/offline stress, boot with SMT limits, kexec/kdump, XIVE and XICS systems, doorbell IPI tests, NMI IPI behavior, and POWER9 HMI setup are useful signals.
