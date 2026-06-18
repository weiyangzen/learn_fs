# sources/distributed-fs/ceph-client/arch/x86/kernel/kvm.c

Purpose: Implements the x86 guest-side KVM paravirtual platform. It detects KVM, enables paravirt clock and platform hooks, manages async page faults, steal time, PV EOI, PV IPIs, PV TLB flush, PV spinlocks, SEV migration/shared-page state, reboot/suspend cleanup, and halt-poll control.

Important APIs/types/functions: exports `kvm_para_available()`, `kvm_arch_para_hints()`, `kvm_async_pf_task_wait_schedule()`, `kvm_read_and_reset_apf_flags()`, haltpoll functions, and `x86_hyper_kvm`. Key flows include `kvm_guest_init()`, `kvm_init_platform()`, `kvm_guest_cpu_init()`, `kvm_guest_cpu_offline()`, `__kvm_handle_async_pf()`, `sysvec_kvm_asyncpf_interrupt()`, `kvm_flush_tlb_multi()`, `__send_ipi_mask()`, `kvm_spinlock_init()`, and SEV helpers.

Control flow: CPUID detection finds the KVM signature. Platform init sets SEV page encryption callbacks, resets KVM shared-page state for encrypted guests, initializes kvmclock, APIC post-init, and guest MTRR state. Late guest init installs reboot/syscore hooks, initializes async-PF sleeper hash locks, enables steal-time static calls and PV spinlock preemption tests, installs PV EOI and async-PF interrupt vector, replaces SMP hooks for PV TLB/IPI/yield where supported, and registers CPU hotplug callbacks. Per-CPU init writes KVM MSRs for async PF, PV EOI, steal time, migration control, and clock.

State and persistence: persistent runtime state is per-CPU decrypted `apf_reason`, `steal_time`, `kvm_apic_eoi`, `async_pf_enabled`, hash-table async-PF sleepers, static keys, and paravirt/static-call registrations. State must be disabled before reboot, kexec, CPU offline, suspend, or crash because the host keeps writing registered guest physical addresses.

Dependencies and integration points: depends on KVM CPUID/MSR ABI, x86 paravirt ops, APIC callbacks, SMP ops, CPU hotplug, kvmclock, e820/MTRR, confidential-computing memory encryption APIs, EFI SEV migration variable, syscore suspend/resume, reboot notifiers, qspinlock PV hooks, and haltpoll.

Risks: async PF injected with interrupts disabled or in kernel mode panics because the host violated the ABI. Shared per-CPU structures must be decrypted before exposing physical addresses under SEV. PV TLB flush relies on steal-time preempted flags and must queue flush-on-enter for preempted vCPUs. Reboot/kexec cleanup is required to prevent host writes into freed memory.

Test signals: KVM guest boot should show expected paravirt features, kvmclock, steal time, and PV EOI when advertised. Tests should cover `no-kvmapf`, `no-steal-acc`, CPU hotplug, suspend/resume, kexec/crash shutdown, async PF wait/wake including wake-before-wait dummy entries, SEV/SEV-ES/SNP migration control, PV IPI clusters, PV TLB with preempted vCPUs, and haltpoll enable/disable.
