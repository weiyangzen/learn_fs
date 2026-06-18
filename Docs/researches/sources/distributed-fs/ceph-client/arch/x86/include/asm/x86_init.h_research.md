<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/x86_init.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/x86_init.h

Purpose: Defines x86 platform initialization and runtime callback tables. It is the main contract by which native PC, hypervisor, encrypted guest, ACPI, PCI, timer, interrupt, memory-resource, and CPU hotplug code override default x86 behavior without hard-coding platform tests at every call site.

Important APIs/types/functions: `struct x86_init_ops`, `x86_init_resources`, `x86_init_mpparse`, `x86_init_irqs`, `x86_init_oem`, `x86_init_paging`, `x86_init_timers`, `x86_init_iommu`, `x86_init_pci`, `x86_hyper_init`, `x86_init_acpi`, `x86_cpuinit_ops`, `x86_platform_ops`, `x86_hyper_runtime`, `x86_guest`, `x86_apic_ops`, `x86_legacy_features`, `x86_legacy_i8042_state`; globals `x86_init`, `x86_cpuinit`, `x86_platform`, `x86_msi`, `x86_apic_ops`; no-op helpers such as `x86_init_noop`, `bool_x86_init_noop`, `set_rtc_noop`, and `get_rtc_noop`.

Control flow: Early boot code and subsystem initializers call through these tables after platform detection has installed the right callbacks. The flow is deliberately indirect: MP table parsing, ROM/resource reservation, interrupt mode selection, page-table setup, timer/wallclock setup, ACPI root pointer handling, PCI initialization, hypervisor late init, CPU hotplug clock setup, and encrypted-memory transitions all dispatch through function pointers.

State and persistence behavior: Persistent state is the global callback tables and embedded legacy-feature flags. Guest encryption callbacks coordinate private/shared memory transitions and kexec conversion windows but do not store memory metadata themselves. Runtime wallclock, sched clock, NMI, APIC, IOMMU shutdown, and real-mode trampoline hooks mutate external platform state.

Dependencies and integration points: Forward declarations touch `ghcb`, `pt_regs`, `cpuinfo_x86`, `irq_domain`, and ACPI/PCI/interrupt concepts. Integrates with boot setup, SMP hotplug, APIC/MSI, ACPI, paravirtualization, SEV/TDX-style confidential computing, PAT, real-mode trampoline, RTC/wallclock, and x86 legacy device probing.

Risks and test signals: Main risks are NULL or stale callback wiring, wrong boot ordering, and platform callbacks that violate early-boot constraints. Test with native PC boot, Xen/KVM guest boot, SEV/TDX memory encryption transitions, CPU hotplug, PCI/MSI enumeration, ACPI reduced-hardware boot, kexec, suspend/resume, and builds across 32-bit, 64-bit, SMP, ACPI, PCI, and hypervisor configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/x86_init.h -->
