# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_mdio.c

## Purpose
Implements the MDIO bus backend for the Synopsys ARC EMAC driver. It allocates and registers a `struct mii_bus`, provides PHY register read/write callbacks through ARC EMAC registers, and optionally toggles a PHY reset GPIO from device-tree properties.

## Important APIs, Types, and Functions
Key entry points are `arc_mdio_probe()` and `arc_mdio_remove()`, exported to the ARC EMAC core through `emac.h`. `arc_mdio_read()` and `arc_mdio_write()` implement `mii_bus` callbacks by programming `R_MDIO`; `arc_mdio_complete_wait()` polls `R_STATUS & MDIO_MASK` and clears completion bits; `arc_mdio_reset()` handles `phy-reset-gpios` style reset through `devm_gpiod_get_optional()`. State is held in `struct arc_emac_priv`, especially `priv->bus` and `priv->bus_data`.

## Control Flow and State
Probe allocates a bus, assigns callbacks, reads optional `phy-reset-duration`, resolves either an `mdio` child node or the EMAC node for backwards compatibility, and registers the bus with `of_mdiobus_register()`. Reads and writes synchronously issue encoded MDIO commands and wait up to about one second. Removal unregisters and frees the bus and clears `priv->bus`.

## Dependencies and Integration Points
Depends on the ARC register helpers (`arc_reg_get()`, `arc_reg_set()`), OF MDIO registration, GPIO descriptors, and PHYLIB consumers above it. Device-tree compatibility is important because old nodes without an `mdio` subnode are still accepted.

## Risks and Test Signals
Timeout handling is the primary failure mode; tests should exercise missing PHYs, slow MDIO completion, and reset GPIO polarity/timing. The reset duration clamp appears suspicious: values over 1000 ms are set to `1`, not `1000`, so board files with large values get an unexpectedly tiny reset pulse. Useful signals include successful PHY discovery, `ethtool` MII access, and no leaked bus after probe failures.
