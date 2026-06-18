<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/terastation_pro2-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/terastation_pro2-setup.c

### Purpose
`terastation_pro2-setup.c` initializes Buffalo Terastation Pro II/Live boards.

### Important APIs, Types, And Functions
Important functions are `tsp2_init()`, `tsp2_pci_preinit()`, `tsp2_pci_map_irq()`, `tsp2_pci_init()`, `tsp2_power_off()`, and UART microcontroller helpers. The file defines NOR flash, PCI IRQ GPIO, Ethernet data, RTC I2C data, MPP modes, and a machine descriptor.

### Control Flow
Subsystem PCI init configures the PCI IRQ GPIO as level-low and registers common Orion PCI host setup. Board init calls common Orion setup, configures MPP, maps/registers NOR flash, initializes USB/Ethernet/I2C/UARTs, configures RTC IRQ, registers I2C RTC, and installs UART1 microcontroller power-off.

### State, Persistence, And Dependencies
Persistent effects include GPIO IRQ setup, PCI host registration, platform flash registration, I2C RTC info, UART1 state during shutdown, and power-off callback. Dependencies include physmap flash, mv643xx Ethernet, I2C, serial register access, and common Orion setup.

### Integration Points
The ATAGS `MACHINE_START(TERASTATION_PRO2, ...)` descriptor wires this board to common Orion map/IRQ/timer/restart/fixup hooks.

### Risks
Power-off depends on an ACK/checksum protocol over UART1 and has limited retry handling. PCI IRQ mapping assumes a single slot at offset 7 with GPIO 11. RTC IRQ failure only warns.

### Test Signals
Boot should enumerate PCI SATA controller, flash, Ethernet, USB, UARTs, and RTC, and shutdown should power off through the microcontroller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/terastation_pro2-setup.c -->
