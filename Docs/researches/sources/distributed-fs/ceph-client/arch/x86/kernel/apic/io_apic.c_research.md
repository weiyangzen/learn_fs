# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/io_apic.c

## Purpose
This is the main IO-APIC implementation. It discovers/registers IO-APICs, maps their MMIO windows, saves/restores redirection entries, maps GSIs and MP/ACPI interrupt source records to Linux IRQs, creates hierarchical irqdomains, configures route entries, handles masking/unmasking/EOI/affinity, probes timer routing, and supports hotplug registration/unregistration.

## Important APIs, Types, And Functions
Core state includes `ioapics[]`, `nr_ioapics`, `gsi_top`, `mp_irqs[]`, `mp_irq_entries`, `ioapic_is_disabled`, `io_apic_irqs`, and `ioapic_dynirq_base`. Key structures are `irq_pin_list`, `mp_chip_data`, `mp_ioapic_gsi`, and per-IOAPIC `struct ioapic`. Externally relevant functions include `disable_ioapic_support()`, `mp_save_irq()`, `arch_early_ioapic_init()`, `native_io_apic_read()`, `clear_IO_APIC()`, `save_ioapic_entries()`, `mask_ioapic_entries()`, `restore_ioapic_entries()`, `acpi_get_override_irq()`, `ioapic_set_alloc_attr()`, `mp_map_gsi_to_irq()`, `mp_unmap_irq()`, `IO_APIC_get_PCI_irq_vector()`, `enable_IO_APIC()`, `restore_boot_irq_mode()`, `setup_IO_APIC()`, `io_apic_init_mappings()`, `ioapic_insert_resources()`, `mp_find_ioapic()`, `mp_find_ioapic_pin()`, `mp_register_ioapic()`, `mp_unregister_ioapic()`, and `mp_irqdomain_*`.

## Control Flow
Firmware parsers call `mp_register_ioapic()` and `mp_save_irq()` during enumeration. Early IRQ init allocates saved RTE storage. Mapping code creates fixmaps and resources. `enable_IO_APIC()` detects any ExtINT pin and clears all non-SMI RTEs. `setup_IO_APIC()` creates irqdomains, fixes IDs, syncs arbitration IDs, maps MP interrupt source pins, initializes traps, and verifies timer IRQ routing via `check_timer()`.

Runtime allocation maps GSIs through `mp_map_gsi_to_irq()`, which locates IO-APIC/pin, derives polarity/trigger attributes, allocates from the IO-APIC irqdomain, and configures `mp_chip_data`. Activation calls `ioapic_configure_entry()`, which asks the parent MSI/vector domain to compose a message and copies the resulting fields into the RTE. Affinity changes call the parent chip then rewrite the RTE. Level EOI handling uses local APIC TMR state and IO-APIC EOI or mask/edge/level simulation to clear remote IRR.

## State And Persistence
The file persists firmware routing records, IO-APIC hardware metadata, saved RTE snapshots for suspend/resume and IRQ remapping transitions, IRQ-to-pin lists for shared mappings, and per-IRQ route attributes. Syscore suspend/resume saves/restores RTEs and IO-APIC IDs. Hotplug registration updates `gsi_top`, fixmaps, resources, and irqdomains.

## Dependencies And Integration Points
It integrates with MP table/ACPI parsing, irqdomain hierarchy, vector domain, interrupt remapping, legacy PIC, LAPIC setup, PCI routing, HPET/timer code, syscore PM, memblock/fixmap/resource management, and confidential-computing MMIO encryption decisions.

## Risks
Risks concentrate around firmware quirks and interrupt races: broken MP tables, duplicate IO-APIC IDs, overlapping GSI ranges, remote-IRR not clearing, timer IRQ misrouting, non-atomic RTE updates, shared ISA pins, interrupt remapping transitions, and CPU affinity moves. Incorrect lock ordering around `ioapic_lock`/`ioapic_mutex` or route-entry write order can produce lost or stuck interrupts.

## Test Signals
Inspect `apic=debug` IO-APIC dumps, GSI-to-IRQ mappings, timer boot probes, `/proc/interrupts`, PCI MSI/MSI-X routing with and without IRQ remapping, suspend/resume, CPU hotplug, `noapic`, ACPI override behavior, and hotplug IO-APIC register/unregister paths.
