<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c64xx.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c64xx.h

### Purpose
Defines S3C64xx physical address and virtual address mappings for legacy board and SoC code.

### Important APIs, Types, And Functions
Macros cover S3C64xx system controller, GPIO, VICs, SROM/memory controller, modem, watchdog, USB high-speed PHY, DMA, SDHCI, SPI, framebuffer, I2C, and media peripheral physical bases, plus virtual aliases such as `S3C64XX_VA_GPIO` and `S3C64XX_VA_MODEM`.

### Control Flow
No runtime flow. `s3c64xx.c` turns selected constants into `map_desc` entries and platform resources use the physical bases.

### State, Persistence, And Dependencies
No mutable state. It depends on the shared map base layout and S3C64xx hardware address map.

### Integration Points
Used by register headers, S3C64xx common init, power management, and device resource declarations.

### Risks
The register macros assume the mapped virtual ranges exist early. Device driver resources and static maps must stay consistent or drivers may access unmapped or wrong regions.

### Test Signals
Successful UART, GPIO, VIC, timer, USB PHY, and SDHCI initialization on S3C6410 hardware are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s3c64xx.h -->
