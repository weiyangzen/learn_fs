<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/kurobox_pro-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/kurobox_pro-setup.c

### Purpose
`kurobox_pro-setup.c` initializes Buffalo/Revogear Kurobox Pro and Buffalo Linkstation Pro/Live Orion5x boards.

### Important APIs, Types, And Functions
Important functions are `kurobox_pro_init()`, `kurobox_pro_pci_init()`, `kurobox_pro_power_off()`, and UART microcontroller helpers `kurobox_pro_miconread/write/send()`. The file defines NOR/NAND flash resources, Ethernet/I2C/SATA data, MPP modes, and two machine descriptors.

### Control Flow
PCI init disables legacy PCI for Kurobox Pro, then registers common PCIe/PCI host setup. Board init calls common Orion init, configures MPP, initializes USB, Ethernet, I2C, SATA, UARTs, XOR, maps/registers NOR and optionally NAND, registers RTC board info, and registers a UART1 microcontroller power-off callback.

### State, Persistence, And Dependencies
State persists in platform devices, MBUS device-bus windows, I2C RTC registration, UART1 configuration during power-off, and registered power-off callback. Dependencies include physmap flash, Orion NAND, mv643xx Ethernet, SATA, I2C, serial registers, and common Orion setup.

### Integration Points
`MACHINE_START()` entries wire the same init function to Kurobox Pro and Linkstation Pro/Live when their configs are enabled.

### Risks
Power-off hijacks UART1 and assumes a specific microcontroller ACK/checksum protocol. PCI is explicitly disabled for Kurobox Pro even though the common descriptor still has two controllers. NAND registration only occurs on the Kurobox machine check.

### Test Signals
Boot should expose NOR, optional NAND, Ethernet, SATA, USB, RTC, and UARTs. Shutdown should send microcontroller commands and power off reliably.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/kurobox_pro-setup.c -->
