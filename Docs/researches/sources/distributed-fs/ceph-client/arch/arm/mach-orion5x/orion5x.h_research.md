<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/orion5x.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/orion5x.h

### Purpose
`orion5x.h` defines Orion5x physical/virtual address maps, peripheral register bases, device-bus registers, and supported device/revision IDs.

### Important APIs, Types, And Functions
It defines bases and sizes for on-chip registers, PCIe/PCI IO and memory windows, crypto SRAM, device bus, bridge, PCI, PCIe, USB, XOR, Ethernet, SATA, crypto, GPIO, SPI, I2C, UART, MPP registers, and device IDs/revisions for MV88F5181, MV88F5182, MV88F5281, and MV88F6183.

### Control Flow
There is no executable flow. The macros are address and identity constants.

### State, Persistence, And Dependencies
The header has no state and includes `irqs.h` for platform IRQ definitions.

### Integration Points
Common init, board files, PCI, IRQ, MPP, watchdog, and peripheral registration all use these constants.

### Risks
Address-map constants underpin static mappings and MBUS windows; mistakes can break all device access. Device/revision IDs drive clock and erratum decisions.

### Test Signals
Successful boot with working serial, timer, PCI, Ethernet, USB, SATA, and restart validates the map indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/orion5x.h -->
