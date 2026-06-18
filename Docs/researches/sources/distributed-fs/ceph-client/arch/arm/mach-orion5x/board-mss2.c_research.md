<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-mss2.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-mss2.c

### Purpose
`board-mss2.c` supplies Maxtor Shared Storage II board-specific PCI and power-off handling.

### Important APIs, Types, And Functions
Key functions are `mss2_pci_map_irq()`, `mss2_pci_init()`, `mss2_power_off()`, and `mss2_init()`. It defines an `hw_pci` descriptor using common Orion PCI setup and scan functions.

### Control Flow
PCI init runs as a subsystem initcall for the ATAGS MSS2 machine. DT board init can call `mss2_init()`, which registers a power-off callback. The callback enables reset output and asserts CPU soft reset, relying on U-Boot to enter an idle mode on next boot.

### State, Persistence, And Dependencies
Persistent effects are PCI host registration and reset-control register writes during power-off. Dependencies include common Orion PCI, bridge reset registers, and platform power-off registration.

### Integration Points
`board-dt.c` invokes `mss2_init()` for `maxtor,shared-storage-2`; ATAGS code uses `machine_is_mss2()` for PCI init.

### Risks
Power-off is implemented as a reboot into bootloader-managed idle state, so it depends on userspace/U-Boot environment preparation. PCI IRQ mapping adds no board-specific fallback beyond common Orion.

### Test Signals
MSS2 boot should initialize PCI only on the correct machine, and shutdown should reset into the expected U-Boot idle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-mss2.c -->
