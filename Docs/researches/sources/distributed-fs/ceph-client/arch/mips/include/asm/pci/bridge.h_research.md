# sources/distributed-fs/ceph-client/arch/mips/include/asm/pci/bridge.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/pci/bridge.h

### Purpose
`bridge.h` is the SGI SN/IP27 Bridge/XBridge PCI-GIO-to-Xtalk ASIC contract. It maps the Bridge register file with `struct bridge_regs`, defines ATE, PIO, DMA, interrupt, response-buffer, reset, device-window, and error bit layouts, and carries the per-controller state shape used by PCI host bridge code.

### Important APIs, Types, And Functions
Key types are `struct bridge_regs`, `struct bridge_err_cmdword`, and `struct bridge_controller`. Important macros include `mkate`, `BRIDGE_INTERNAL_ATES`, the `BRIDGE_*` register offsets, ISR/IMR/IRR error groups, `BRIDGE_DEV_*` device-window attributes, PCI/GIO/Xtalk alias ranges, DMA range tests such as `IS_PCI32_MAPPED`, `BRIDGE_CONTROLLER(bus)`, and raw register helpers `bridge_read`, `bridge_write`, `bridge_set`, and `bridge_clr`.

### Control Flow
This header has no standalone runtime loop. Drivers include it, cast mapped Bridge MMIO to `struct bridge_regs`, then program register fields using raw reads/writes. PCI enumeration uses the Type 0/Type 1 config windows, DMA setup uses ATE/direct-map constants, interrupt setup writes destination and mask registers, and error handlers decode ISR/error command words into fatal, dumpable, or clearable groups.

### State, Persistence, Dependencies, And Integration
State lives in Bridge hardware registers, SSRAM/ATE RAM, PCI configuration space, IRQ domains, and `struct bridge_controller` instances attached to `pci_bus->sysdata`; nothing is filesystem-persistent. Dependencies include `linux/types.h`, `linux/pci.h`, Xtalk widget definitions, SGI SN `nasid_t`, raw I/O accessors, resources, and IRQ domains. The header integrates SGI Xtalk fabric, PCI core, GIO compatibility, DMA mapping, and interrupt routing; Ceph depends on it only indirectly through a working MIPS kernel platform.

### Risks
The register struct and offset macros must remain byte-exact; padding mistakes corrupt MMIO. Raw read-modify-write helpers are not locked and can race with IRQ or concurrent device setup. DMA address range macros assume Bridge address decoding and `PHYS_RAMBASE` semantics. Fatal-error masks are platform-policy sensitive, and misclassified errors can either panic unnecessarily or hide bus corruption.

### Test Signals
Build SGI SN/IP27 PCI configurations, compare `offsetof(struct bridge_regs, field)` with the `BRIDGE_*` constants, boot with PCI devices behind Bridge, exercise config cycles, DMA mapping, interrupts, and induced PCI/Xtalk errors, and run sparse/build warnings for pointer/address-width mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pci/bridge.h -->
