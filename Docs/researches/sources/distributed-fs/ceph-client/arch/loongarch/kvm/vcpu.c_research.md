# sources/distributed-fs/ceph-client/arch/loongarch/kvm/vcpu.c

Purpose: implements the LoongArch KVM vCPU lifecycle, run loop, ioctl register ABI, CPUID mapping, guest/host CSR save/restore, auxiliary FPU/vector/LBT/PMU ownership, PV time, interrupts, and statistics.

Important APIs, types, and functions: public KVM arch hooks include `kvm_arch_vcpu_create()`, `kvm_arch_vcpu_destroy()`, `kvm_arch_vcpu_load()`, `kvm_arch_vcpu_put()`, `kvm_arch_vcpu_ioctl_run()`, `kvm_arch_vcpu_ioctl()`, `kvm_arch_vcpu_unlocked_ioctl()`, reg/FPU/mpstate/debug ioctl helpers, `kvm_arch_vcpu_runnable()`, `kvm_get_vcpu_by_cpuid()`, `kvm_own_fpu()`, `kvm_lose_fpu()`, optional LSX/LASX/LBT ownership, and stats descriptors.

Control flow: the run path completes outstanding MMIO/IOCSR/hypercall exits, loads vCPU state, checks signals and KVM requests, delivers interrupts/exceptions, checks VPID, performs late aux/TLB requests with IRQs disabled, enters guest via `kvm_loongarch_ops->enter_guest()`, and handles exits through the assembly/C loop. ioctl paths read/write GPRs, CSRs, CPUCFG, LBT, KVM counter/debug/reset registers, PV feature attributes, and PV time GPA. Load/put restore/save large sets of guest hardware CSRs and timer state and handle per-CPU `last_vcpu` caching.

State and persistence: per-vCPU state includes GPRs, PC, CSR array, CPUID map entry, FPU/vector/LBT state, PMU state, timer, MMU cache, pending IRQ/exception bitmaps, PV steal-time cache, last CPU, VPID, and aux flags. Per-VM CPUID map and PV feature flags are also mutated.

Dependencies and integration points: integrates with `switch.S`, `exit.c`, `interrupt.c`, `timer.c`, `tlb.c`, `main.c`, generic KVM ioctls, dirty ring, xfer-to-guest work, scheduler steal-time accounting, CPUID/CPUCFG hardware feature probes, and tracepoints.

Risks: CSR save/restore completeness is critical for migration and correctness. Aux ownership must not leak host FPU/vector/LBT/PMU state. CPUID uniqueness is protected by a spinlock and rejects runtime changes. PV feature consistency is enforced VM-wide. The run loop has delicate IRQ/preempt state transitions.

Test signals: KVM API selftests for one-reg/CPUCFG/CSR/FPU/mpstate/debug/interrupt ioctls, guest boot and migration, FPU/LSX/LASX/LBT workloads, PMU passthrough, PV time/preempt tests, dirty ring exits, and CPU hotplug/migration stress.
