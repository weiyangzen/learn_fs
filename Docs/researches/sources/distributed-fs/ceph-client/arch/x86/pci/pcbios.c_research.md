<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/pcbios.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/pcbios.c

## Purpose
`pcbios.c` implements BIOS32 and PCI BIOS support for legacy x86 PCI config access and IRQ routing. It scans low BIOS memory for the BIOS32 service directory, invokes real firmware entry points through far calls, optionally installs PCI BIOS raw config ops, and exposes BIOS IRQ routing APIs.

## Important APIs, types, and functions
Important functions include `set_bios_x()`, `bios32_service()`, `check_pcibios()`, `pci_bios_read()`, `pci_bios_write()`, `pci_find_bios()`, `pcibios_get_irq_routing_table()`, `pcibios_set_irq_routing()`, and `pci_pcbios_init()`. Data includes `bios32_indirect`, `pci_indirect`, `pcibios_enabled`, `pci_bios_present`, and the BIOS raw ops table.

## Control flow
`pci_pcbios_init()` runs when `PCI_PROBE_BIOS` is enabled. It scans `0xe0000-0xfffff` for a valid `_32_` structure, marks BIOS memory executable, locates the `$PCI` service, calls the BIOS present function, validates the PCI signature and version, updates direct-probe masks for supported hardware mechanisms, and installs BIOS config access. IRQ helpers later call BIOS functions to fetch routing options or set a hardware interrupt line.

## State and persistence behavior
BIOS entry pointers are stored in kernel virtual form with kernel code/data segments. Enabling PCI BIOS marks the low BIOS area RWX and sets `pcibios_enabled`. `pci_bios_present` gates routing calls. `pcibios_last_bus` may be populated from BIOS present output.

## Dependencies and integration points
It integrates with low-memory mappings, x86 segment descriptors, `pci_config_lock`, PCI BIOS function numbers, PCI IRQ routing in `irq.c`, direct-probe fallback selection, and boot option `pci=nobios`.

## Risks and edge cases
Running BIOS code after kernel boot is inherently risky and leaves a RWX BIOS hole unless disabled. Firmware may return bogus signatures, nonzero carry status, unmasked read data, high-memory BIOS32 entries, or routing tables larger than a page. The implementation warns that modern systems should prefer MMCONFIG/direct access.

## Test signals
Legacy BIOS machines, `pci=biosirq`, `pci=nobios`, systems lacking direct mechanism support, IRQ routing table fetches, and NX/RWX log messages are relevant. Confirm config reads/writes serialize under `pci_config_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/pcbios.c -->
