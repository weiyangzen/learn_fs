<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/intel_mid.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/intel_mid.c

## Purpose
`intel_mid.c` supplies PCI access, IRQ, power, and fixed-BAR behavior for Intel MID/Moorestown-style SoCs where many devices use MMCONFIG, selected Lincroft devices also require type-1 writes, and some non-existent type-1 config accesses can hang hardware.

## Important APIs, types, and functions
Core helpers include `fixed_bar_cap()`, `pci_device_update_fixed()`, `type1_access_ok()`, custom `pci_read()`/`pci_write()`, `intel_mid_pci_irq_enable()`, `intel_mid_pci_irq_disable()`, `intel_mid_pci_init()`, `pci_d3delay_fixup()`, `mid_power_off_devices()`, and `pci_fixed_bar_fixup()`. The file defines MID PCI ops and CPU/device IDs for Silvermont MID plus Merrifield MMC/HSU quirks.

## Control flow
`intel_mid_pci_init()` installs custom root PCI ops, initializes late ECAM, replaces IRQ enable/disable hooks, marks SoC mode, and disables ACPI IRQ routing. Reads use type-1 only for known safe bus-0 devices/registers; other accesses go through `raw_pci_ext_ops`. Writes ignore ROM BARs, synthesize fixed-BAR sizing writes when a vendor extended capability advertises fixed sizes, and otherwise choose safe type-1 or MMCONFIG. IRQ enable maps PCI interrupt-line GSIs directly to IO-APIC IRQs with model-specific polarity and IRQ0 exceptions.

## State and persistence behavior
`pci_soc_mode` gates final/header fixups in kernels that also run on non-SoC systems. Fixed-BAR fixups rewrite resource ends and mark BARs `IORESOURCE_PCI_FIXED`. MID power-off fixups push known LSS devices into D3hot by updating PMCSR; actual power removal happens elsewhere.

## Dependencies and integration points
It depends on ECAM setup, direct config ops, IO-APIC GSI mapping, ACPI no-IRQ mode, Intel MID power island IDs, IOSF-era device topology, PCI extended capabilities, and generic PCI fixup stages.

## Risks and edge cases
Access filtering must never type-1 probe absent Lincroft devices. Fixed-BAR size synthesis assumes power-of-two size descriptors and a read immediately after a `~0` sizing write. IRQ0 handling is device-specific and can silently leave bogus devices without an interrupt. `pci_soc_mode` must be correct before fixups run.

## Test signals
Boot on Moorestown/Merrifield/Tangier hardware, BAR sizing on fixed-BAR devices, IRQ allocation for MMC and HSU devices, suspend/power-island behavior, and absence of hangs when scanning non-existent functions are primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/intel_mid.c -->
