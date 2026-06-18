<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-setup.c -->
## sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-setup.c

### Purpose
`malta-setup.c` performs Malta platform memory and device setup after PROM initialization. It installs DT data, reserves standard IO resources, configures DMA/coherency, PCI clock hints, optional floppy and VGA console setup, and board quirks.

### Important APIs, Types, And Functions
`get_system_type()` returns `"MIPS Malta"`. `plat_get_fdt()` returns `__dtb_start`. `plat_mem_setup()` is the main setup routine. Helpers include `plat_setup_iocoherency()`, `pci_clock_check()`, `bonito_quirks_setup()`, `fd_activate()`, and optional `screen_info_setup()`.

### Control Flow
`plat_mem_setup()` obtains and shims the FDT, calls `__dt_setup_arch()`, initializes PCI BIOS, inserts standard PC IO resources, enables DMA channel 4, applies Bonito debug/coherency quirks, detects IOCU/Bonito hardware coherency, appends `pci_clock=` when jumpers report a non-33 MHz PCI clock, and sets up optional floppy/VGA state.

### State, Persistence, And Dependencies
Persistent state includes DT setup, IO resource reservations, DMA default coherency, PCI command-line updates, SuperIO state, and screen info. Dependencies include Malta revision state, firmware command line, Bonito/ROCit registers, PCI, DMA, and optional console/floppy drivers.

### Integration Points
This file connects early Malta controller setup with generic PCI, DMA, DT, console, and platform device probing.

### Risks
Command-line mutation must fit available buffer space. Coherency detection changes DMA behavior globally. IOCU disabled by switch falls back to software coherency. PCI clock hints affect IDE timing and must not duplicate user-supplied `pci_clock=`.

### Test Signals
Boot Malta under Bonito and IOCU-capable ROCit, check DMA coherency mode logs, PCI enumeration, `pci_clock=` command line, resource reservations, floppy activation, and VGA console registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mti-malta/malta-setup.c -->
