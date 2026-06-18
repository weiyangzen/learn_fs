<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-s3c64xx-dt.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-s3c64xx-dt.c

### Purpose
Provides the flattened-device-tree machine descriptor for Samsung S3C64xx systems.

### Important APIs, Types, And Functions
`s3c64xx_dt_map_io()` initializes early debug I/O, maps common S3C64xx I/O, and sets the timer source to PWM3/PWM4. `DT_MACHINE_START(S3C6400_DT, ...)` binds compatible strings `samsung,s3c6400` and `samsung,s3c6410`.

### Control Flow
On DT boot, the machine descriptor calls the map callback before normal OF platform population. Interrupt and device discovery are delegated to DT-aware irqchip, pinctrl, clock, and platform code rather than legacy board files.

### State, Persistence, And Dependencies
No persistent state. It relies on `debug_ll_io_init()`, `s3c64xx_init_io()`, and `s3c64xx_set_timer_source()`.

### Integration Points
Used instead of `s3c64xx.c` legacy board setup when booting with populated DT. It shares common I/O mapping and timer variant setup with non-DT paths.

### Risks
Only the map/timer base setup is done here; missing DT nodes or drivers will not be compensated by legacy platform devices. The machine name says S3C6400 but covers S3C6410 too.

### Test Signals
DT boot should reach console output, initialize timer/clocksource, and populate devices from compatible DT nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/mach-s3c64xx-dt.c -->
