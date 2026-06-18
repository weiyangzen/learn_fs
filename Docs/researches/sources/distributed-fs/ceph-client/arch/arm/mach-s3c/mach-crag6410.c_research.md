<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410.c

### Purpose
Provides the legacy non-DT machine description and board data for the Wolfson Cragganmore 6410 development board.

### Important APIs, Types, And Functions
Static board data describes UARTs, PWM backlight, LCD panel timing, keypad matrix, GPIO keys, DM9000 Ethernet, MMGPIO, fixed regulators, WM831x PMICs, I2C devices, SDHCI hosts, LEDs, DWC2 OTG, and SPI chip selects. Important functions are `crag6410_lcd_power_set()`, `crag6410_map_io()`, `crag6410_cfg_sdhci0()`, and `crag6410_machine_init()`. `MACHINE_START(WLF_CRAGG_6410, ...)` wires the machine to S3C6410 IRQ, mapping, timer, and init callbacks.

### Control Flow
`crag6410_map_io()` maps S3C64xx I/O, sets the 12 MHz crystal, registers UART configs, and selects PWM timers. `crag6410_machine_init()` sets pull-ups and initial GPIO output states, installs platform data for SDHCI/I2C/framebuffer/USB/keypad/SPI, registers I2C board info and GPIO lookup tables, adds PWM lookup entries and platform devices, registers MMGPIO and LEDs, enforces regulator constraints, then initializes S3C64xx PM.

### State, Persistence, And Dependencies
State is static platform data consumed by legacy platform drivers. Runtime side effects configure GPIO direction, pull state, platform device lists, I2C/SPI child devices, regulator constraints, and PM domains. Dependencies span S3C64xx SoC helpers, Samsung framebuffer/SDHCI/I2C/SPI/keypad APIs, gpiolib lookup tables, regulators, WM831x PMIC data, DM9000, DWC2, LED, GPIO-key, and PWM subsystems.

### Integration Points
This board file anchors non-DT Cragganmore boot. It interacts with `mach-crag6410-module.c` through registered `"wlf-gf-module"` I2C devices and depends on S3C6410 CPU init, IRQ setup, and clock/timer initialization.

### Risks
Most behavior is encoded in static platform data, so address, IRQ, GPIO, or regulator mistakes surface only at boot on hardware. GPIO requests do not consistently check errors. Several devices depend on PMIC IRQ-base arithmetic and board-specific lookup names matching driver expectations.

### Test Signals
A successful boot should enumerate I2C/SPI codecs, PMIC regulators, SDHCI, framebuffer/backlight, keypad, DM9000, DWC2, LEDs, and suspend/resume. Hardware smoke tests should check LCD power, SD card detection, module detection, and regulator dependency ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-crag6410.c -->
