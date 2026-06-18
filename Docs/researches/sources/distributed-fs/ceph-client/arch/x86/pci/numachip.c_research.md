<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/numachip.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/numachip.c

## Purpose
`numachip.c` provides Numascale NumaConnect-specific PCI config accessors derived from x86_64 ECAM, with an extra guard that prevents AMD Northbridges from decoding bus-0 accesses to non-existent devices in remote I/O configurations.

## Important APIs, types, and functions
The central functions are `pci_mmcfg_read_numachip()`, `pci_mmcfg_write_numachip()`, `pci_dev_base()`, and `pci_numachip_init()`. The raw ops table `pci_mmcfg_numachip` is installed for both normal and extended config access. File-local `limit` records the highest bus-0 devfn allowed.

## Control flow
Initialization reads AMD Northbridge register `0x60` at bus 0 device 0x18 function 0. Bits 6:4 describe fabric size; the resulting number of northbridges determines the first disallowed devfn. Reads and writes reject bus 0 accesses at or beyond `limit`, returning all ones for reads and dropping writes, otherwise using normal ECAM lookup and MMIO access.

## State and persistence behavior
`limit` is read-mostly and persists after init. Global `raw_pci_ops` and `raw_pci_ext_ops` are replaced with Numachip ops. Per-region mapping state remains owned by the shared MMCONFIG layer.

## Dependencies and integration points
It depends on preexisting ECAM region mappings, raw config read during init, AMD northbridge layout, and Numachip platform detection code that calls `pci_numachip_init()`.

## Risks and edge cases
If fabric-size decoding is wrong, valid devices can disappear or unsafe accesses can still reach absent northbridges. The special guard only applies to bus 0; other buses use ordinary ECAM behavior. Initialization must run after raw PCI reads are possible.

## Test signals
Boot on Numascale hardware, scan bus 0 around the northbridge limit, verify no machine checks or remote decode issues, and confirm normal ECAM access continues for valid devices and nonzero buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/numachip.c -->
