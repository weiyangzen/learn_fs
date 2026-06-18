## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/mdio.c

Purpose: implements v2 MDIO bus access, PHY discovery/connection, and PHY link adjustment.

Important APIs, types, and functions: the file configures MII management clocking, waits for `MII_MGMT_BUSY` to clear, implements MDIO read/write through MAC management registers, registers an `mii_bus`, connects the netdev PHY, and tears the bus down. The link adjustment callback updates `pdata->phy_speed`, disables the MAC, calls `xge_mac_set_speed`, re-enables the MAC, and reports link changes through netdev/PHY helpers.

Control flow, state, and persistence: `xge_probe` calls `xge_mdio_config` after hardware reset. On open, `phy_start` begins PHY state machine callbacks. On close/remove, `phy_stop` and MDIO removal disconnect and unregister the bus. Current negotiated speed persists in `pdata->phy_speed`.

Dependencies and integration points: depends on PHYLIB/MDIO APIs, OF/ACPI device properties, MAC register definitions in `mac.h`, CSR access in `enet.c`, and netdev lifecycle in `main.c`.

Risks: MDIO busy polling has bounded wait loops; hung hardware can fail reads/writes. Link adjustment reprograms MAC while traffic may be active, so ordering with PHY state and MAC enablement matters. Probe requires a valid PHY attachment for useful link behavior.

Test signals: `mdiobus` registration, PHY probe, `ethtool` link settings, forced speed/duplex changes, cable unplug/replug, and MDIO timeout fault injection.
