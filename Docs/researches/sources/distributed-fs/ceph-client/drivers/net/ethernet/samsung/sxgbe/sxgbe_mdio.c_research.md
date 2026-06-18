# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_mdio.c

Purpose: Provides SXGBE MDIO bus access and registration. It bridges PHYLIB `mii_bus` operations to the controller's SMA/MDIO registers for Clause 22 and Clause 45 PHY transactions.

Important APIs and flow: `sxgbe_mdio_busy_wait()` polls the data register busy bit for up to three seconds. `sxgbe_mdio_ctrl_data()` builds the command word using the access command, skip-address-frame bit, `priv->clk_csr`, payload, and busy bit. Clause-specific helpers program address/data registers. `sxgbe_mdio_read_c22()`, `sxgbe_mdio_write_c22()`, `sxgbe_mdio_read_c45()`, and `sxgbe_mdio_write_c45()` are installed into `struct mii_bus`. `sxgbe_mdio_register()` allocates and registers the bus, scans discovered PHYs, assigns probed IRQs when requested, auto-selects `plat->phy_addr` when unset, and stores `priv->mii`. `sxgbe_mdio_unregister()` unregisters and frees it.

State and dependencies: The bus uses the netdev as `bus->priv`, platform `sxgbe_mdio_bus_data` for masks/IRQs, `priv->hw->mii` register offsets initialized by `sxgbe_get_ops()`, and `priv->clk_csr` from platform or dynamic clock-rate selection. It mutates `plat->phy_addr` when the MAC did not specify one.

Risks and test signals: Clause 22 access rejects PHY addresses 4 and above, so board data must match hardware limitations. Busy-wait timeout, missing `mdio_bus_data`, and no-PHY discovery are key failure paths. Tests should exercise C22/C45 reads and writes, phy mask behavior, probed IRQ assignment, auto phy address selection, timeout injection, unregister without register, and probe failure after successful `mdiobus_register()`.
