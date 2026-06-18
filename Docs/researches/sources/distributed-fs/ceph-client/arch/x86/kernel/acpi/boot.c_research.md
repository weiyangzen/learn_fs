# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/boot.c

## Purpose
`boot.c` is the x86 architecture ACPI boot integration layer. It maps early ACPI tables, interprets MADT/FADT/HPET/BOOT/BGRT/SPCR data, chooses the IRQ routing model, enumerates LAPIC/x2APIC/SAPIC and IOAPIC topology, wires ACPI GSI registration into PIC or IOAPIC backends, and applies old-platform DMI quirks. It is reached from `setup_arch()` through `acpi_boot_table_init()`, `early_acpi_boot_init()`, and `acpi_boot_init()`, so most state here is early boot state that becomes global policy for SMP, interrupt routing, PCI initialization, sleep, and ACPI OS services.

## Important APIs, Types, and Functions
- Global policy/export state: `acpi_disabled`, `acpi_pci_disabled`, `acpi_noirq`, `acpi_lapic`, `acpi_ioapic`, `acpi_strict`, `acpi_disable_cmcff`, `acpi_irq_model`, `acpi_int_src_ovr[]`, `acpi_sci_flags`, `acpi_sci_override_gsi`, `isa_irq_to_gsi[]`, and the function pointers `__acpi_register_gsi`, `__acpi_unregister_gsi`, `acpi_suspend_lowlevel`.
- Table mapping: `__acpi_map_table()` and `__acpi_unmap_table()` wrap `early_memremap()` and `early_memunmap()` for the ACPI core.
- MADT CPU parsing: `acpi_parse_madt()`, `acpi_parse_lapic()`, `acpi_parse_x2apic()`, `acpi_parse_sapic()`, NMI parsers, `acpi_is_processor_usable()`, and `topology_register_apic()` integration.
- MADT IRQ parsing: `acpi_parse_ioapic()`, `acpi_parse_int_src_ovr()`, `acpi_sci_ioapic_setup()`, `mp_override_legacy_irq()`, `mp_register_ioapic_irq()`, and `mp_config_acpi_legacy_irqs()`.
- Public IRQ APIs: `acpi_gsi_to_irq()`, `acpi_isa_irq_to_gsi()`, `acpi_register_gsi()`, `acpi_unregister_gsi()`, `acpi_register_ioapic()`, `acpi_unregister_ioapic()`, and `acpi_ioapic_registered()`.
- CPU hotplug APIs under `CONFIG_ACPI_HOTPLUG_CPU`: `acpi_map_cpu()` and `acpi_unmap_cpu()`.
- Boot sequence APIs: `acpi_boot_table_init()`, `early_acpi_boot_init()`, `acpi_boot_init()`, `acpi_mps_check()`, and command-line parsers for `acpi=`, `pci=`, `acpi_sci=`, `bgrt_disable`, and timer-override knobs.
- Miscellaneous ACPI OS hooks: global-lock helpers `__acpi_acquire_global_lock()`/`__acpi_release_global_lock()`, `arch_reserve_mem_area()`, RSDP getters/setters, Xen PV `acpi_os_ioremap`, and `acpi_get_cpu_uid()`.

## Control Flow
Early flow starts in `acpi_boot_table_init()`, which runs the early DMI blacklist, bails out if ACPI was already disabled, locates initial tables, and reserves them. `early_acpi_boot_init()` completes table initialization, parses the Simple Boot Flag table, checks `acpi_blacklisted()`, parses MADT enough to register the LAPIC base, and applies reduced-hardware initialization. Later, `acpi_boot_init()` reruns SBF parsing, parses FADT for legacy-device and PM-timer state, fully processes MADT CPU and IOAPIC entries, parses optional HPET and BGRT tables, installs `pci_acpi_init` unless ACPI IRQ routing is disabled, and parses SPCR for early console setup.

MADT processing first validates the LAPIC/x2APIC/SAPIC CPU entries and records usable processors even when disabled so hotplug capacity can be sized. It then parses IOAPIC entries, interrupt source overrides, synthetic SCI setup if firmware did not provide an override, legacy ISA mappings, and NMI sources. When both LAPIC and IOAPIC paths succeed, `acpi_set_irq_model_ioapic()` switches `acpi_irq_model` from PIC to IOAPIC and replaces the GSI registration function pointers.

Runtime registration flow is intentionally indirect. `acpi_register_gsi()` dispatches through `__acpi_register_gsi`, which initially points to `acpi_register_gsi_pic()` and later points to `acpi_register_gsi_ioapic()` after IOAPIC discovery. IOAPIC mapping is serialized by `acpi_ioapic_lock` and uses irqdomain allocation metadata derived from ACPI trigger/polarity. CPU and IOAPIC hotplug APIs similarly translate ACPI handles and GSIs into APIC IDs, NUMA nodes, and IOAPIC registrations.

## State and Persistence Behavior
Most variables are boot-time or `__initdata` state, but their effects persist through global exported flags, APIC topology tables, the IRQ model, registered IOAPICs, `isa_irq_to_gsi[]`, platform legacy-device flags, the ACPI PM timer port, HPET resource insertion, and the ACPI suspend low-level function pointer. DMI quirks and command-line options can permanently disable all ACPI, ACPI PCI routing, XSDT use, BGRT parsing, or SCI polarity/trigger defaults for the boot. The ACPI global lock helpers operate on firmware-shared lock words using `try_cmpxchg`.

## Dependencies and Integration Points
This file sits between the ACPICA table parser and x86 subsystems: APIC topology, IOAPIC irqdomains, PCI IRQ routing, HPET, BGRT, SPCR serial console, e820/NVS reservation, Xen PV ioremap behavior, ACPI hotplug CPU/IOAPIC paths, NUMA node assignment, legacy PIC/ELCR, DMI, and platform legacy device descriptors. It calls into `madt_wakeup.c` through `acpi_parse_mp_wake()` when `CONFIG_ACPI_MADT_WAKEUP` is enabled and into `sleep.c` through `x86_acpi_suspend_lowlevel`.

## Risks
- Invalid or inconsistent MADT entries can disable ACPI or leave the system in PIC mode; regressions here affect boot CPU enumeration and interrupt delivery very early.
- IRQ source override handling is quirk-heavy, especially IRQ0 and SCI trigger/polarity. Small changes can break old BIOSes or produce interrupt storms.
- `__acpi_register_gsi` function-pointer switching is global; using it before the IRQ model is finalized or without the IOAPIC lock can produce mismatched IRQ mappings.
- DMI blacklist and command-line parsing decisions override large subsystems; changes require care because the affected hardware is often old and hard to test.
- Hardware-reduced ACPI bypasses legacy PIC/timer setup, so legacy assumptions can fail on those platforms.

## Test Signals
- Boot logs should report MADT LAPIC/IOAPIC use, HPET base, PM timer port, SCI override behavior, and any DMI quirks.
- Kernel boot tests should cover `acpi=off`, `acpi=force`, `acpi=noirq`, `pci=noacpi`, `acpi=rsdt`, `acpi_sci=edge/level/high/low`, and timer override options.
- x86 ACPI hotplug tests should exercise CPU map/unmap and IOAPIC register/unregister paths.
- Interrupt routing validation should include legacy PIC fallback, IOAPIC systems with interrupt source overrides, and hardware-reduced ACPI systems.
