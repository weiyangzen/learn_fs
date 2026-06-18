# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_mdio.h

Purpose: Declares MDIO lifecycle helpers for the Sunplus driver.

Important APIs: `spl2sw_mdio_init()` registers the hardware-backed MDIO bus; `spl2sw_mdio_remove()` unregisters it.

State and dependencies: Operates on `struct spl2sw_common`, filling and clearing `comm->mii_bus`. Must be called after registers/clocks/reset are ready and before PHY connection.

Risks and test signals: Return type is `u32` despite returning negative errno values; callers currently store it in `int`. Build and runtime tests should cover missing `mdio` node, probe defer from PHY children, and unregister on partial probe failure.
