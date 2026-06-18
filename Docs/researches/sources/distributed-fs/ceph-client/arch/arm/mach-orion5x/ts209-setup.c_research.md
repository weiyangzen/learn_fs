<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts209-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts209-setup.c

### Purpose
`ts209-setup.c` initializes QNAP TS-109/TS-209 Orion5x boards.

### Important APIs, Types, And Functions
Key functions are `qnap_ts209_init()`, `qnap_ts209_pci_preinit()`, `qnap_ts209_pci_map_irq()`, and `qnap_ts209_pci_init()`. It defines NOR partitions, PCI IRQ GPIOs, RTC data, GPIO keys, SATA data, MPP modes, and a machine descriptor.

### Control Flow
PCI init configures two PCI interrupt GPIOs and registers common Orion PCI setup. Board init calls common Orion setup, configures MPP, maps/registers NOR flash, initializes USB, reads the MAC address from the NAS Config partition through shared TSx09 code, initializes Ethernet/I2C/SATA/UARTs/XOR, registers keys, configures RTC IRQ, registers I2C RTC, and installs shared QNAP power-off.

### State, Persistence, And Dependencies
State persists in flash platform data, PCI IRQ GPIOs, Ethernet MAC platform data, buttons, RTC IRQ, SATA platform data, and power-off callback. Dependencies include common Orion PCI/init, `tsx09-common`, physmap flash, SATA, I2C, and GPIO keys.

### Integration Points
The ATAGS machine descriptor uses common Orion hooks and the shared QNAP TSx09 helper for MAC and power-off.

### Risks
Flash partition order intentionally differs from physical order for firmware compatibility. PCI IRQ slot offsets are board-specific. Power button is handled by the PIC microcontroller rather than GPIO keys.

### Test Signals
Boot should expose correct MTD partitions, PCI devices, SATA ports, Ethernet MAC, USB copy/reset buttons, RTC IRQ, and shared QNAP power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts209-setup.c -->
