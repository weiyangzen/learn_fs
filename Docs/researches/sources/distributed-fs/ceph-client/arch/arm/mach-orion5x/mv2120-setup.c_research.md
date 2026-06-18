<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mv2120-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mv2120-setup.c

### Purpose
`mv2120-setup.c` initializes HP Media Vault mv2120/mv5100 board devices.

### Important APIs, Types, And Functions
Key functions are `mv2120_init()` and `mv2120_power_off()`. The file defines NOR flash partition/resource data, Ethernet/SATA platform data, GPIO buttons, RTC I2C info, GPIO LEDs, MPP modes, and the `MACHINE_START(MV2120, ...)` descriptor.

### Control Flow
Init calls common Orion setup, configures MPP, initializes USB, Ethernet, I2C, SATA, UART, XOR, maps/registers NOR flash, registers buttons, configures RTC IRQ, registers I2C RTC, registers LEDs, requests the power-off GPIO, and registers the power-off callback.

### State, Persistence, And Dependencies
Persistent state includes registered platform devices, GPIO LED/button/power-off configuration, I2C RTC info, and MBUS flash mapping. Dependencies include physmap flash, mv643xx Ethernet, SATA, GPIO keys/LEDs, and Orion common init.

### Integration Points
The machine descriptor wires the setup into legacy ATAGS boot and uses common Orion IRQ/timer/restart/fixup hooks.

### Risks
Power-off drives GPIO 19 low after initializing it high; wrong polarity would prevent shutdown. RTC IRQ setup failure only warns through missing IRQ behavior.

### Test Signals
Boot should expose NOR flash, buttons, LEDs, RTC IRQ, Ethernet, SATA, USB, and reliable GPIO-based power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mv2120-setup.c -->
