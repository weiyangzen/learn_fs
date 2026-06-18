<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-dt.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-dt.c

### Purpose
`board-dt.c` provides the flattened device-tree machine descriptor and common DT initialization path for Orion5x systems.

### Important APIs, Types, And Functions
Important objects/functions are `orion5x_auxdata_lookup`, `orion5x_dt_init()`, `orion5x_dt_compat`, and `DT_MACHINE_START(ORION5X_DT, ...)`.

### Control Flow
DT init identifies the SoC and TCLK, initializes MBUS from DT, sets up PCI/PCIe windows, applies the 88F5281 D0 WFI workaround, runs optional board hooks for MSS2 and d2 Network compatibles, and populates DT platform devices with auxdata names for legacy drivers.

### State, Persistence, And Dependencies
State persists in MBUS windows, CPU idle polling mode, and populated platform devices. Dependencies include OF platform population, MVEBU MBUS, Orion mapping/restart functions, and optional board-specific hooks.

### Integration Points
This is the DT machine entry for `"marvell,orion5x"` and calls common Orion setup while avoiding ATAGS board descriptors.

### Risks
`BUG_ON(mvebu_mbus_dt_init(false))` turns MBUS init failure into a hard boot stop. Auxdata keeps legacy driver naming assumptions alive and must match physical addresses.

### Test Signals
DT boot should identify the SoC, populate SPI/I2C/watchdog/SATA/crypto devices, and execute optional compatible-specific board hooks only on matching boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/board-dt.c -->
