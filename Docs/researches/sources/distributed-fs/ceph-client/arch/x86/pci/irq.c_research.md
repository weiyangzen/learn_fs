<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/irq.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/irq.c

## Purpose
`irq.c` implements legacy x86 PCI INTx routing using BIOS `$PIR` tables, AMI `$IRT` conversion, PCI BIOS fallback, chipset-specific PIRQ routers, ELCR programming, DMI workarounds, and IO-APIC fallback for devices not handled by ACPI/MSI.

## Important APIs, types, and functions
Key data structures are `struct irq_router`, `struct irq_router_handler`, global `pirq_table`, `pirq_router`, `pirq_router_dev`, `pcibios_irq_mask`, and `pirq_penalty[16]`. Public hooks are `pcibios_enable_irq`, `pcibios_disable_irq`, `pcibios_irq_init()`, `pcibios_fixup_irqs()`, `pcibios_penalize_isa_irq()`, `elcr_set_level_irq()`, and `mp_should_keep_irq()`. Router handlers cover Intel PIIX/ICH/PCEB/IB, VIA, ALI/FinALi, SiS, VLSI, ServerWorks, AMD756, OPTi, ITE, Cyrix, PicoPower, and optional PCI BIOS routing.

## Control flow
Boot scans BIOS memory for `$PIR`, then byte scans for `$IRT` and converts it if needed. If a table exists, peer buses are scanned, a router device is found by table vendor/device or fallback device matching, and exclusive IRQs penalize unavailable lines. IRQ lookup resolves a device pin, swizzles through bridges if needed, applies DMI quirks, chooses an existing or lowest-penalty IRQ, programs router links and ELCR level mode, then propagates the chosen IRQ to devices sharing the same PIRQ link. IO-APIC mode bypasses the PIRQ table and maps bus/slot/pin vectors instead.

## State and persistence behavior
State persists in global routing-table pointers, router function tables, DMI flags for broken HP/Acer systems, ELCR programmed mask, IRQ penalties, `dev->irq`, and `dev->irq_managed`. BIOS-converted routing tables are allocated dynamically and freed when IO-APIC routing makes them unnecessary.

## Dependencies and integration points
The file integrates with raw PCI config access, PCI BIOS services, DMI, ACPI IRQ penalty routing, IO-APIC MP-table vector lookup, ISA ELCR ports, chipset config-space or port-I/O registers, `x86_init.pci.fixup_irqs()`, and the PCI core enable/disable IRQ hooks.

## Risks and edge cases
Legacy routing relies on firmware tables that may contain wrong links, masks, router IDs, or bus numbers. Router register programming is chipset-specific and often undocumented. Penalty choices affect shared ISA/PCI IRQ stability. Bridge swizzling and shared-PIRQ propagation can misroute multifunction or bridge-hidden devices. Disable must preserve IRQs during system suspend and runtime suspend preparation.

## Test signals
Use old BIOS-only systems, `pci=biosirq`, `pci=routeirq`, `pci=usepirqmask`, IO-APIC disabled/enabled boots, DMI-quirked laptops, and drivers using legacy INTx. Logs showing PIRQ table discovery, router selection, ELCR changes, and INTx-to-IRQ mappings are key evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/irq.c -->
