# sources/distributed-fs/ceph-client/arch/x86/kernel/x86_init.c

Purpose: defines default x86 initialization, CPU-init, platform, and APIC operation tables. These tables provide standard PC behavior while allowing platform, hypervisor, or vendor code to override hooks during boot.

Important APIs/functions: exports `x86_platform`. Defines noop helpers, `x86_wallclock_init()`, `x86_init`, `x86_cpuinit`, `x86_platform`, and `x86_apic_ops`. Default hooks cover resources, MP parsing, IRQ setup, OEM setup, paging, timers, IOMMU, PCI, hypervisor hooks, ACPI root pointer handling, RTC access, sched_clock suspend/restore, real mode, memory encryption transitions, and IO-APIC access.

Control flow: static table initialization wires defaults such as ROM probing, E820 memory setup, DMI setup, IOAPIC/native IRQ init, HPET timer init, APIC clock setup, native page-table init, CMOS wallclock, native CPU/TSC calibration, and real-mode reservation. `x86_wallclock_init()` checks a device-tree CMOS node and replaces RTC hooks with noops when disabled.

State and persistence: the operation tables are global boot-time state. `x86_platform` and `x86_apic_ops` are `__ro_after_init`, so overrides must happen before the read-only-after-init transition. Noop functions avoid null checks for absent platform capabilities.

Dependencies and integration: central integration point for architecture setup code, `tsc.c`, HPET/RTC, ACPI, PCI, APIC/IOAPIC, DMI, E820, paravirt/hypervisor hooks, memory encryption guest operations, realmode setup, and IOMMU shutdown.

Risks: wrong defaults or late overrides can route core boot operations to invalid handlers. Because many subsystems call through these tables, ABI compatibility of hook signatures and init ordering is critical.

Test signals: boot on standard PC, ACPI, devicetree RTC-disabled, hypervisor, encrypted guest, and PCI/IOAPIC configurations. TSC calibration should use the native hooks unless a platform overrides them.
