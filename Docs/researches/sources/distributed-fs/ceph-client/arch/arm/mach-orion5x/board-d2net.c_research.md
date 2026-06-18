<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-d2net.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-d2net.c

### Purpose
`board-d2net.c` adds DT-era board-specific setup for LaCie d2 Network and Big Disk Network LEDs.

### Important APIs, Types, And Functions
The exported init hook is `d2net_init()`. Internal pieces are `d2net_gpio_leds_init()`, GPIO LED platform data, and a GPIO lookup table mapping blue and red front LEDs.

### Control Flow
Init configures a CPLD blink-control GPIO so the blue LED can blink with SATA activity, adds lookup entries for `leds-gpio`, registers the LED platform device, and logs that flash writes are unsupported.

### State, Persistence, And Dependencies
Persistent state is GPIO direction/value and the registered `leds-gpio` platform device. Dependencies include Orion GPIO, gpiod lookup tables, and the generic LED GPIO driver.

### Integration Points
`board-dt.c` calls `d2net_init()` when the DT compatible string is `lacie,d2-network`.

### Risks
GPIO request failures only log and continue, potentially leaving LEDs in bootloader state. The setup assumes specific CPLD wiring outside the DT description.

### Test Signals
Booting a d2 Network DT should register two front LEDs and show expected SATA blink behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-d2net.c -->
