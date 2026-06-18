<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/net2big-setup.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/net2big-setup.c

### Purpose
`net2big-setup.c` initializes the LaCie 2Big Network NAS.

### Important APIs, Types, And Functions
Important functions are `net2big_init()`, `net2big_sata_power_init()`, `net2big_gpio_leds_init()`, and `net2big_power_off()`. It defines NOR flash, Ethernet, I2C, SATA, GPIO LED/key data, MPP modes, and machine descriptor data.

### Control Flow
Init calls common Orion setup, configures MPP, initializes USB/Ethernet/I2C/UART/XOR, powers up SATA disks through CPLD GPIO sequencing, initializes SATA, maps/registers NOR flash, registers buttons and LEDs, registers I2C RTC/EEPROM devices, marks high GPIOs valid, configures power-off GPIO, and logs flash-write limitations.

### State, Persistence, And Dependencies
State persists in GPIO directions/values, registered platform devices, I2C board info, MBUS windows, and power-off callback. Dependencies include Orion GPIO, physmap flash, mv643xx Ethernet, SATA, I2C boardinfo, GPIO keys/LEDs, and CPLD-specific wiring.

### Integration Points
The `MACHINE_START(NET2BIG, ...)` descriptor uses this setup under legacy ATAGS boot with common Orion hooks.

### Risks
SATA power sequencing depends on 300 ms CPLD timing and high-numbered GPIO validity. Several LED/SATA GPIO setup failures log and continue. NOR partition is marked read-only pending write support validation.

### Test Signals
Boot should power both disks, register SATA, show correct front/SATA LEDs and rocker-switch inputs, expose RTC/EEPROM, and power off via GPIO 24.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/net2big-setup.c -->
