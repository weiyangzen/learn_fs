<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_64.c

## Purpose
`mmconfig_64.c` implements the x86_64 ECAM accessor. Unlike 32-bit, it maps each ECAM window persistently and allows lockless MMIO config-space access protected by RCU lookup and shared-region lifetime rules.

## Important APIs, types, and functions
Important functions are `pci_dev_base()`, `pci_mmcfg_read()`, `pci_mmcfg_write()`, `mcfg_ioremap()`, `pci_mmcfg_arch_map()`, `pci_mmcfg_arch_unmap()`, `pci_mmcfg_arch_init()`, and `pci_mmcfg_arch_free()`. The exported raw ops table is `pci_mmcfg`.

## Control flow
Architecture init maps every region in `pci_mmcfg_list`; any mapping failure frees all previously mapped regions and reports failure. Reads/writes validate bounds, find a mapped base with RCU, compute `virt + bus offset + devfn offset + reg`, and perform byte/word/dword MMIO access. Hotplug insert/delete uses the same map/unmap helpers.

## State and persistence behavior
Each `struct pci_mmcfg_region` stores `virt`, a virtual base biased so bus offsets can be applied uniformly. Unmap calls `iounmap()` on the real mapped start and clears `virt`. Raw extended ops persist globally after successful arch init.

## Dependencies and integration points
It depends on the shared ECAM region list, `ioremap()`, RCU, x86 MMIO config accessors, and generic PCI raw extended config operations. Hotplug region insertion from ACPI root handling also uses these map routines.

## Risks and edge cases
Persistent mappings consume virtual address space proportional to bus coverage. RCU readers require deletion to synchronize before freeing. Incorrect bus-range biasing would produce wrong config addresses. Reads from absent mappings return all ones and `-EINVAL`, matching PCI config failure semantics.

## Test signals
Validate extended capability access on multiple segments, ECAM windows starting at nonzero bus numbers, hotplug insertion/deletion, mapping failure paths, and concurrent config-space readers during hostbridge removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_64.c -->
