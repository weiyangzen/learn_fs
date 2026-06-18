## sources/distributed-fs/ceph-client/arch/mips/pci/pci-generic.c

### Purpose
This file supplies generic MIPS PCI BIOS helpers for systems using the newer generic host-bridge path. It aligns resources, fixes up bridge bus resources, and optionally remaps I/O space.

### Important APIs, Types, And Functions
`pcibios_align_resource()` handles ISA-style I/O mirroring avoidance and delegates to a host bridge `align_resource` hook or generic `pci_align_resource()`. `pcibios_fixup_bus()` reads bridge bases. Under `pci_remap_iospace`, `pci_remap_iospace()` maps a physical I/O range and calls `set_io_port_base()`.

### Control Flow
Resource alignment first rounds I/O starts out of mirrored 0x100-0x3ff modulo ranges. It then finds the host bridge for the device and delegates when available. Memory resources use generic PCI alignment. I/O remapping accepts only a zero-based resource and installs the mapped virtual base globally.

### State, Persistence, And Dependencies
State effects are the global MIPS I/O port base and resource start choices made during PCI assignment. Dependencies are Linux PCI host-bridge helpers, `ioremap()`, and MIPS I/O-port base support.

### Integration Points
The file is used by generic PCI drivers such as `PCI_DRIVERS_GENERIC` systems. It complements platform files that register host bridges using standard Linux PCI APIs rather than legacy `pci_controller`.

### Risks
`pci_remap_iospace()` rejects nonzero I/O resource starts, so device-tree ranges must match this assumption. Resource alignment can surprise devices expecting dense I/O packing.

### Test Signals
Check assigned I/O BARs avoid mirrored ranges, host-specific alignment callbacks run when installed, and `pci_remap_iospace()` produces working inb/outb access for generic host bridges.
