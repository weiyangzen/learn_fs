# sources/distributed-fs/ceph-client/arch/x86/kernel/devicetree.c

## Purpose
Adds x86 Open Firmware/devicetree boot support, especially for Intel CE4100-style APIC, HPET, PCI, CPU, and platform-device discovery.

## Important APIs, Types, And Functions
`add_dtb()` records setup-data DTB address. `x86_flattree_get_config()` maps, verifies, unflattens, and installs DT SMP parsing. `x86_of_pci_init()` replaces PCI IRQ hooks. `dtb_lapic_setup()`, `dtb_cpu_setup()`, and `dtb_ioapic_setup()` configure APICs. `dt_irqdomain_alloc()` converts DT IO-APIC firmware specifiers into mp irqdomain allocations.

## Control Flow
Early boot records DTB data pointer, maps enough bytes to read total FDT size, verifies and copies the tree, then, when ACPI is disabled and DT exists, replaces MP-table parsing with DT parsing. DT parsing configures HPET address, LAPIC address/mode, CPU APIC IDs and NUMA nodes, and IO-APIC domains. Later device init probes compatible CE4100 buses and PCI IRQ enable maps DT PCI interrupts.

## State, Persistence, And Dependencies
State includes `initial_dtb`, `cmd_line`, `of_ioapic`, registered APIC/IO-APIC state, HPET address, PCI IRQ hooks, and populated OF nodes. It depends on OF/FDT, APIC/IO-APIC, irqdomain, PCI, HPET, ACPI-disabled mode, and NUMA helpers.

## Integration Points
Bridges devicetree into x86 SMP discovery, PCI IRQ assignment, platform device creation, and interrupt domain allocation.

## Risks
Malformed DT interrupt parameters or missing APIC IDs break interrupt routing. Mapping only the initial DTB window requires correct `fdt_totalsize()`. This path is sensitive to ACPI-vs-DT boot mode.

## Test Signals
DT-booted x86 should populate devices, register LAPIC/IO-APIC, assign PCI IRQs through OF, and avoid MP-table parsing when ACPI is disabled.
