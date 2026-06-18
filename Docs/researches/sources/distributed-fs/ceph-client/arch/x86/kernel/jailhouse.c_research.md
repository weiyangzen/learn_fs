# sources/distributed-fs/ceph-client/arch/x86/kernel/jailhouse.c

Purpose: Implements x86 hypervisor detection and paravirtual platform setup for Jailhouse non-root cells. It replaces normal firmware, ACPI, SMP, PCI, timer, and restart assumptions with values supplied through Jailhouse setup data.

Important APIs/types/functions: main externally visible pieces are `jailhouse_paravirt()` and `x86_hyper_jailhouse`. Internal setup flows include `jailhouse_cpuid_base()`, `jailhouse_init_platform()`, `jailhouse_parse_smp_config()`, `jailhouse_pci_arch_init()`, `jailhouse_timer_init()`, `jailhouse_serial_workaround()`, and `jailhouse_no_restart()`. Static state is `setup_data` and `precalibrated_tsc_khz`.

Control flow: detection checks CPUID hypervisor leaves for the `Jailhouse` signature. Platform init overrides `x86_init` and `x86_platform` hooks, disables legacy PIC and ACPI, walks boot `setup_data` records to find `SETUP_JAILHOUSE`, validates version and size, then stores PM timer, APIC frequency, TSC frequency, PCI MMCONFIG, CPU IDs, and UART flags. SMP parsing registers LAPIC address, per-cell APIC IDs, optional IOAPIC, and legacy UART IRQs. PCI init enables direct config access and full root-bus scan because Jailhouse cells have no bridge topology.

State and persistence: state is boot-time only. Jailhouse-provided setup data is copied into a static structure and used to seed kernel platform globals such as `pmtmr_ioport`, `lapic_timer_period`, `pcibios_last_bus`, `pci_probe`, and TSC-known-frequency capability.

Dependencies and integration points: integrates with the x86 hypervisor table, APIC/x2APIC selection, mptable/IOAPIC registration, PCI direct/MMCONFIG code, serial 8250 ISA configurator, reboot machine ops, and ACPI disable path.

Risks: invalid or incompatible setup data panics early. x2APIC must use physical mode because interrupt remapping is unavailable. Version 1 UART handling assumes legacy IRQ mapping, while version 2 can selectively disable inaccessible UART ports. Restart is unsupported and halts instead.

Test signals: booting a Jailhouse non-root Linux cell should detect the hypervisor, avoid ACPI-table complaints, register the supplied CPU IDs and IOAPIC, set known TSC frequency, scan virtual PCI devices, and enforce UART access flags. Unsupported setup-data versions should panic with the expected message.
