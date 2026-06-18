<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/fixup.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/fixup.c

## Purpose
`fixup.c` is the x86 PCI quirk table for hardware and firmware defects that must be corrected during PCI enumeration, enable, suspend, resume, or final setup. It does not provide a single driver; it registers many `DECLARE_PCI_FIXUP_*` callbacks that alter device resources, config registers, power-management capabilities, bus operations, host-bridge windows, and platform-specific reserved regions.

## Important APIs, types, and functions
Important callbacks include `pci_fixup_i450nx()`, `pci_fixup_i450gx()`, `pci_fixup_umc_ide()`, `pci_fixup_via_northbridge_bug()`, `pcie_rootport_aspm_quirk()`, `pci_xeon_x2_bifurc_quirk()`, `pci_fixup_video()`, Toshiba OHCI1394 pre/post fixups, `sb600_disable_hpet_bar()`, `pci_amd_enable_64bit_bar()`, `rs690_fix_64bit_dma()`, ChromeOS L1SS save/restore helpers, `asus_disable_nvme_d3cold()`, and AMD root-port PME suspend/resume quirks. The file uses PCI core fixup registration macros, DMI matching tables, resource APIs, raw I/O ports, HPET state, VGA arbitration, AMD SMN access, and suspend helpers.

## Control flow
The PCI core invokes callbacks at declared phases. Early/header fixups correct discovery inputs such as bogus BARs, secondary buses, ROM shadows, HPET BARs, transparent bridges, or non-compliant BAR sizing. Final fixups mutate post-enumeration policy such as PME support, D3cold permissions, root-window resources, MRRS limits, and bus operation wrappers. Suspend/resume fixups restore firmware-clobbered registers or temporarily mask broken PME states before system sleep.

## State and persistence behavior
Most changes persist in `struct pci_dev` fields or device config space. File-local state includes ASPM offsets per root port, saved Toshiba cache-line size, AMD 64-bit root-window `struct resource`, saved ChromeOS L1SS capability headers, and cached PME support restored from config space. Some changes reserve global address ranges through `request_mem_region()` or add resources to root buses. Quirks are deliberately idempotent where they run at resume.

## Dependencies and integration points
This file sits between PCI core enumeration, architecture PCI helpers, DMI, VGA arbitration, HPET, suspend, AMD node/SMN support, resource management, and platform firmware behavior. It affects downstream drivers by changing BAR ownership, link power management, PME capabilities, IRQ-visible resources, and hotplug child-bus config writes.

## Risks and edge cases
Quirk match scope is the main risk: a too-broad vendor/device match can damage unrelated hardware, while too-narrow DMI matching leaves machines broken. Config-space writes can race with firmware expectations across suspend/resume. The ASPM bus-op replacement assumes bounded root-port/device indexing. The AMD root-window workaround taints the kernel and must avoid multisocket systems. PME masking changes wake behavior and must distinguish runtime suspend from system suspend.

## Test signals
Useful signals are PCI enumeration logs, resource tree diffs, suspend/resume on affected DMI systems, ASPM write filtering tests, BAR sizing on listed Intel/AMD chipsets, USB wake validation on AMD SoCs, MacBook/Twinhead reserved-region checks, and no regressions in generic PCI resource assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/fixup.c -->
