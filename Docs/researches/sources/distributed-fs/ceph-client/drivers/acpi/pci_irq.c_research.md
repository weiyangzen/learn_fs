# sources/distributed-fs/ceph-client/drivers/acpi/pci_irq.c

`pci_irq.c` implements ACPI `_PRT` routing for PCI INTx interrupts. It finds routing entries for devices or parent bridges, applies DMI quirks, allocates link-device IRQs or static GSIs, registers/unregisters GSIs, and manages `pci_dev` IRQ state.

Important structures and functions include `struct acpi_prt_entry`, DMI quirk tables, `do_prt_fixups()`, `acpi_pci_irq_check_entry()`, `acpi_pci_irq_find_prt_entry()`, `acpi_pci_irq_lookup()`, optional x86 IO-APIC boot interrupt rerouting, ISA fallback registration, `acpi_pci_irq_valid()`, `acpi_pci_irq_enable()`, and `acpi_pci_irq_disable()`.

Enable flow skips devices without pins or already managed IRQs, resolves direct `_PRT` entries, falls back to parent bridge swizzling/CardBus inheritance, tolerates legacy IDE no-route cases, allocates ACPI PCI link IRQs or uses static GSIs, registers the GSI with model-specific polarity, stores the Linux IRQ, and marks it managed. Disable skips suspend/runtime-suspend cases, re-resolves routing, frees link IRQs if needed, unregisters the GSI, and clears management state.

The file owns only temporary `acpi_prt_entry` allocations. Persistent effects are in ACPI PCI link state, GSI registration, and `pci_dev->irq`/`irq_managed`. Dependencies include ACPICA `_PRT`, PCI core, ACPI PCI links, GSI registration, ISA/EISA fallback, DMI, x86 IO-APIC quirks, runtime PM, and GIC/LPIC polarity policy.

Risks include bad firmware `_PRT` entries, fragile bridge swizzling, fallback masking missing routing, disable failures when routing changes, and preserving IRQ programming during suspend. Test signals include static and link `_PRT`, DMI fixups, ARI, bridge-derived routing, CardBus, legacy IDE, ISA fallback, IO-APIC reroute variants, GIC/LPIC polarity, enable idempotence, and suspend/runtime-suspend disable behavior.
