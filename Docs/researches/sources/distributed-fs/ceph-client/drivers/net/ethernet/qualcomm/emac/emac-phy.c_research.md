# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-phy.c

### Purpose
`emac-phy.c` implements the EMAC MDIO bus adapter and external PHY discovery for Qualcomm EMAC.

### Important APIs, Types, And Functions
The main public API is `emac_phy_config()`. Internal MDIO callbacks are `emac_mdio_read()` and `emac_mdio_write()`, which program `EMAC_PHY_STS` and `EMAC_MDIO_CTRL`, then poll for `MDIO_START`/`MDIO_BUSY` completion.

### Control Flow
`emac_phy_config()` allocates a managed `mii_bus`, fills bus identity/callbacks/parent/private adapter, and registers the bus differently for ACPI and device tree. ACPI registration uses `mdiobus_register()`, reads optional `phy-channel`, and falls back to `phy_find_first()`. Device tree registration uses `of_mdiobus_register()`, reads the `phy-handle` phandle, and resolves it with `of_phy_find_device()`. Failure to find a PHY unregisters the bus and returns `-ENODEV`.

### State, Persistence, And Dependencies
The adapter stores `adpt->mii_bus` and `adpt->phydev`. MDIO transactions use MMIO registers and the adapter base pointer. ACPI paths manually take a reference to match OF helper reference behavior. Dependencies include PHYLIB, OF MDIO, ACPI property helpers, and `readl_poll_timeout()`.

### Integration Points
The platform probe path calls `emac_phy_config()` before MAC bringup. `emac_mac_up()` later connects the discovered `phydev` with `phy_connect_direct()` in SGMII mode and uses PHY callbacks for link changes.

### Risks
MDIO polling timeout units and clock selection must match hardware. ACPI fallback to first PHY can hide bad firmware descriptions. Reference handling must stay balanced with the driver's unload path. Bus unregister on PHY lookup failure is manual despite devm allocation.

### Test Signals
Test ACPI with explicit and missing `phy-channel`, DT with valid/missing `phy-handle`, MDIO read/write timeout injection, no-PHY bus registration, repeated probe/remove, and link negotiation through the discovered PHY.
