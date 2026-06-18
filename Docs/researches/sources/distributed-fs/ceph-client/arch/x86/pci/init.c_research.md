<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/init.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/init.c

## Purpose
`init.c` is the ordered x86 PCI architecture initialization entry point. It sequences direct config-space probing, early ECAM discovery, platform-specific PCI initialization, MSI-domain creation, PCI BIOS fallback, direct-access installation, and DMI PCI-probe quirks.

## Important APIs, types, and functions
The central function is `pci_arch_init()`, registered with `arch_initcall()`. It calls `pci_direct_probe()`, `pci_mmcfg_early_init()`, optional `x86_init.pci.arch_init()`, `x86_create_pci_msi_domain()`, `pci_pcbios_init()`, `pci_direct_init()`, `dmi_check_pciprobe()`, and `dmi_check_skip_isa_align()`. It uses `pci_probe`, `raw_pci_ops`, and `raw_pci_ext_ops`.

## Control flow
Initialization first discovers the direct mechanism type. Unless `PCI_PROBE_NOEARLY` is set, early MCFG/ECAM setup runs before platform overrides. Xen or other platform hooks can then override PCI or MSI behavior through `x86_init.pci.arch_init()`. MSI domains are created after that hook so Xen can replace the creation callback. If platform init allows PCI BIOS probing, BIOS32 probing runs before direct init so legacy probing can still obtain `pcibios_last_bus`.

## State and persistence behavior
The file itself stores no long-lived state, but it establishes global config-access pointers and boot-probe flags. Its ordering determines whether raw config operations, extended config operations, and MSI domains are available to all later PCI scans.

## Dependencies and integration points
It is tightly coupled to `pci/direct.c`, `mmconfig-shared.c`, `pcbios.c`, `x86_init`, IRQ-domain setup, and DMI quirk code. Hypervisors and platform code rely on the `x86_init.pci.arch_init()` insertion point.

## Risks and edge cases
Ordering regressions are high impact: MSI domain creation before Xen setup would allocate the wrong domain, and direct probing before PCI BIOS could lose legacy last-bus information. If no raw or extended config access path is installed, the system logs a fatal PCI access error but boot may continue with no PCI.

## Test signals
Boot with native PCI, Xen PV/HVM, `pci=nobios`, `pci=nommconf`, `pci=noearly`, and old BIOS-only machines. Confirm logs show the intended config-space mechanism and that MSI domains and DMI quirks are initialized in the expected order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/init.c -->
