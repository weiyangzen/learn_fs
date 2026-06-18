# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_common.c

## Purpose
Shared SPARC PCI host-controller support: implements `sun4u_pci_ops` and `sun4v_pci_ops`, imports PBM Open Firmware properties, converts OF `ranges` into Linux resources, reserves virtual-DMA windows, and provides recursive PCI error-status scanners.

## Important APIs, Types, and Functions
`sun4u_config_mkaddr()` builds direct config-space addresses from PBM base, bus, devfn, and register width. `sun4u_read_pci_cfg_host()` / `sun4u_write_pci_cfg_host()` handle host bridge natural-width quirks. `sun4v_read_pci_cfg()` / `sun4v_write_pci_cfg()` proxy config access through hypervisor calls. `pci_get_pbm_props()` imports `bus-range` and `ino-bitmap`. `pci_determine_mem_io_space()` parses OF ranges into `io_space`, `mem_space`, and optional `mem64_space`. Error scanners clear/report target abort, master abort, and parity bits recursively.

## Control Flow
Controller probes populate `pci_pbm_info`, choose sun4u or sun4v ops, then call property/resource helpers. PCI core config accesses enter through the ops. sun4u validates bus range and uses low-level config loads/stores; sun4v builds an HV device id and calls HV wrappers. Controller error handlers call the scanners after latching hardware error registers.

## State and Persistence
Mutates runtime PBM state: bus bounds, `ino_bitmap`, resource descriptors, offsets, config base, and an allocated IOMMU resource descriptor. Error scanners clear PCI status bits. No persistent storage.

## Dependencies and Integration Points
Uses Linux PCI/resource/OF APIs, SPARC PROM halt/printf, low-level config accessors, sun4v HV wrappers, `pci_impl.h`, and generic PCI `struct pci_ops`.

## Risks and Test Signals
Missing OF ranges or MEM/IO windows halt the machine. sun4u host accesses must preserve natural-size behavior. sun4v writes ignore HV errors. Test through boot range logs, successful enumeration, host bridge config reads, and abort/parity bits being reported and cleared.
