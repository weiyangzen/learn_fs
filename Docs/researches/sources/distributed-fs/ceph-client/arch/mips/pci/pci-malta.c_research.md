## sources/distributed-fs/ceph-client/arch/mips/pci/pci-malta.c

### Purpose
This file initializes PCI resources for MIPS Malta-family boards using GT-64120, Bonito64, or MSC/SoC-it controllers. It derives memory and I/O windows from controller registers, fixes controller quirks, and registers the selected `pci_controller`.

### Important APIs, Types, And Functions
Static resources/controllers exist for Bonito64, GT-64120, and MSC. External ops are `bonito64_pci_ops`, `gt64xxx_pci0_ops`, and `msc_pci_ops`. The single entry point `mips_pcibios_init()` selects the controller using `mips_revision_sconid`.

### Control Flow
For GT-64120, the function writes the controller BAR for internal registers, reads memory and I/O decode/remap registers, picks the widest memory window, validates remap masks, and computes offsets. Bonito combines adjacent PCIMAP windows. MSC reads system-controller memory and I/O windows, configures IOCU GCR regions when available, and trims overlapping memory/I/O ranges. All supported controllers set `PCIBIOS_MIN_IO`, adjust global resources, set `io_map_base`, and register the controller.

### State, Persistence, And Dependencies
State is controller hardware register programming, resource window fields, IOCU GCR configuration, and PCI controller registration. Dependencies include Malta board revision IDs, GT64120/Bonito/MSC register APIs, MIPS CPS IOCU support, and legacy PCI core.

### Integration Points
Board setup calls `mips_pcibios_init()` after determining the system controller. Config-space ops are provided by controller-specific files.

### Risks
The code panics with `BUG_ON()` for unsupported discontiguous remaps. It collapses multi-window hardware into one resource, potentially losing usable apertures. Incorrect controller ID detection means no PCI registration.

### Test Signals
Boot on each controller type, inspect computed resource ranges/offsets, enumerate behind bridges, and validate DMA coherency with IOCU-enabled systems.
