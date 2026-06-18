# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx_phy.c

### Purpose
`fec_mpc52xx_phy.c` implements the MDIO bus driver for the MPC5200 FEC MII management interface. It exposes FEC MII read/write operations as a Linux `mii_bus` so PHY devices described under OF can be registered and used by the MPC52xx FEC MAC driver.

### Important APIs, Types, And Functions
`struct mpc52xx_fec_mdio_priv` stores the mapped FEC register block. `mpc52xx_fec_mdio_transfer()` is the core helper: it packs PHY address, register address, and read/write frame bits into `mii_data`, clears the MII event, waits for completion, and returns read data or timeout. `mpc52xx_fec_mdio_read()` and `mpc52xx_fec_mdio_write()` are `mii_bus` callbacks. `mpc52xx_fec_mdio_probe()` allocates the bus/private state, maps registers, sets the bus id, programs `mii_speed`, and calls `of_mdiobus_register()`. Remove unregisters the bus, unmaps registers, and frees state. `mpc52xx_fec_mdio_driver` is exported for registration by `fec_mpc52xx.c`.

### Control Flow
On probe, the driver translates the OF resource, ioremaps it, initializes `bus->read`/`write`, computes MDIO speed from `mpc5xxx_get_bus_frequency()`, registers child PHYs from OF, and stores the bus in device drvdata. Each MDIO operation writes a management frame to the FEC, then polls `FEC_IEVENT_MII` up to three sleep intervals; read operations return the low 16 data bits from `mii_data`.

### State, Persistence, And Dependencies
State is a mapped register pointer plus an allocated `mii_bus`. It depends on OF address/MDIO registration, platform devices, phylib, `asm/mpc52xx.h` bus-frequency helpers, and the MPC52xx FEC register definitions. No state is persisted beyond the registered MDIO bus and hardware registers.

### Integration Points
The MAC driver registers this platform driver before the FEC MAC driver when MDIO support is enabled, ensuring PHY devices exist before MAC open/connect paths need them. Compatible strings include `fsl,mpc5200b-mdio`, `fsl,mpc5200-mdio`, and legacy `mpc5200b-fec-phy`.

### Risks
Timeout behavior is coarse (`msleep(1)` with three tries) and depends on hardware event delivery. The driver uses the FEC register block resource directly, so resource overlap with the MAC node must match platform description. Incorrect MII speed calculation can make all PHY operations unreliable. Error unwinds must free both `priv` and `mii_bus`; current probe funnels most failures through `out_free`.

### Test Signals
Useful tests are OF MDIO node registration, Clause 22 PHY reads/writes, timeout behavior with no responding PHY, module load/unload with the MAC driver, and verifying PHY discovery before FEC open.
