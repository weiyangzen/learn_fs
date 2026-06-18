<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-spi-s3c64xx.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-spi-s3c64xx.c

### Purpose
Provides S3C64xx SPI platform setup for GPIO chip selects and bus configuration.

### Important APIs, Types, And Functions
The exported setup helper configures SPI controller platform data, including chip-select count and GPIO lookup usage.

### Control Flow
Board init calls the setup helper before SPI devices are registered so the controller driver can bind with the correct chip-select topology.

### State, Persistence, And Dependencies
State is platform data attached to the SPI controller plus GPIO lookup entries. Depends on `spi-s3c64xx` platform data and GPIO descriptors.

### Integration Points
Cragganmore calls `s3c64xx_spi0_set_platdata(0, 2)` and registers SPI codec devices.

### Risks
Chip-select numbering and lookup table names must match SPI board info. Wrong CS polarity or count prevents device probing.

### Test Signals
SPI controller probe, CS toggling, and WM0010/Arizona codec SPI transactions validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/setup-spi-s3c64xx.c -->
