# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mdio.c

Purpose: Implements the Sunplus MDIO bus adapter over switch PHY control registers and registers it from the `mdio` device-tree child node.

Important APIs/functions: `spl2sw_mdio_init()` obtains the `mdio` child, allocates a devm `mii_bus`, fills read/write callbacks, registers it with `of_mdiobus_register()`, and stores `comm->mii_bus`. `spl2sw_mdio_remove()` unregisters the bus. `spl2sw_mii_read()` and `spl2sw_mii_write()` call `spl2sw_mdio_access()`. `spl2sw_mdio_access()` temporarily programs `MAC_EXT_PHY0_ADDR`, issues read/write command fields in `L2SW_PHY_CNTL_REG0`, polls `L2SW_PHY_CNTL_REG1`, then restores external PHY0 address to 31 to avoid hardware auto-MDIO side effects.

Control flow and state: MDIO access is serialized with `mdio_lock` around the critical address-select plus command write sequence. The selected external PHY address is transient register state; persistent driver state is only `comm->mii_bus`.

Dependencies and integration points: Integrates Linux MDIO/of_mdiobus with the Sunplus switch register interface. PHY connection in `spl2sw_phy.c` depends on this bus being registered before `of_phy_connect()`.

Risks and test signals: The command completion poll checks `val & cmd`, relying on read-ready/write-done bits matching command values. The address restore occurs after polling without holding `mdio_lock`, so concurrent reads/writes may need scrutiny. Test read/write across both PHY addresses, timeout behavior, concurrent phylib accesses, remove while PHYs are disconnected, and device-tree absence of `mdio`.
