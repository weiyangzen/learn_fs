<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts409-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts409-setup.c

### Purpose
`ts409-setup.c` initializes QNAP TS-409 Orion5x boards.

### Important APIs, Types, And Functions
Key functions are `qnap_ts409_init()`, `qnap_ts409_pci_map_irq()`, and `qnap_ts409_pci_init()`. It defines NOR partition/resource data, RTC info, SATA status LEDs, GPIO keys, MPP modes, and a machine descriptor.

### Control Flow
PCI init registers common Orion PCIe/PCI host setup while board-specific mapping only accepts common PCIe IRQs because legacy PCI is not used. Board init calls common Orion setup, configures MPP, maps/registers NOR flash, initializes USB, reads MAC from NAS Config through shared TSx09 code, initializes Ethernet/I2C/UARTs, registers keys, configures RTC IRQ, registers I2C RTC, registers GPIO LEDs, and installs shared QNAP power-off.

### State, Persistence, And Dependencies
State persists in platform flash/LED/key devices, Ethernet MAC data, RTC IRQ, and power-off callback. Dependencies include common Orion setup, `tsx09-common`, physmap flash, I2C, GPIO LEDs/keys, and PCI core.

### Integration Points
The ATAGS `MACHINE_START(TS409, ...)` descriptor wires this setup into legacy boot and common Orion hooks.

### Risks
PCI legacy bus is unused, so incorrect fallback IRQ mapping would hide problems. Flash partition order is compatibility-sensitive. Power button is outside GPIO key handling.

### Test Signals
Boot should register TS-409 partitions, four SATA status LEDs, reset/copy buttons, Ethernet MAC, RTC IRQ, PCIe SATA controller, and shared power-off behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts409-setup.c -->
