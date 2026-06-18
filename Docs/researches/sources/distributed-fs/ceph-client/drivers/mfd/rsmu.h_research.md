# sources/distributed-fs/ceph-client/drivers/mfd/rsmu.h

### Purpose
`rsmu.h` is the private MFD header shared by the Renesas Synchronization Management Unit core and bus drivers. It declares the common core init/exit functions and defines the ClockMatrix SCSR base address used by bus-specific paged register access.

### Important APIs, Types, And Functions
The header includes the public `linux/mfd/rsmu.h`, defines `RSMU_CM_SCSR_BASE` as `0x20100000`, and declares `rsmu_core_init(struct rsmu_ddata *rsmu)` plus `rsmu_core_exit(struct rsmu_ddata *rsmu)`. It relies on `struct rsmu_ddata` and `enum rsmu_type` from the public header.

### Control Flow
There is no executable control flow. I2C and SPI bus drivers include this file so they can decide when ClockMatrix page registers must be changed and call the shared MFD child registration path after their regmap has been initialized.

### State, Persistence, And Dependencies
The header owns no state. `RSMU_CM_SCSR_BASE` influences persistent hardware register access by telling bus glue not to alter the page register for non-SCSR addresses. Dependencies are the public RSMU MFD header and include guards.

### Integration Points
This is the bridge between `rsmu_core.c`, `rsmu_i2c.c`, and `rsmu_spi.c`. Any change to the SCSR base or core function prototypes affects both bus drivers and all RSMU child devices registered by the core.

### Risks
An incorrect `RSMU_CM_SCSR_BASE` would make I2C/SPI page-selection code write page registers for the wrong address ranges or skip page writes for SCSR registers, causing silent register corruption or failed reads. Since the file only declares APIs, mismatch with public `struct rsmu_ddata` layout would surface at compile time in the bus/core files.

### Test Signals
Compile coverage across `rsmu_core.c`, `rsmu_i2c.c`, and `rsmu_spi.c` is the primary signal. Runtime tests should indirectly validate the base constant by reading and writing ClockMatrix registers below and above `0x20100000` over both I2C and SPI.
