# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mdio.c

## Purpose
`hclge_mdio.c` connects the PF MAC to an external PHY through a Linux `mii_bus` backed by HNS3 firmware command descriptors. It implements Clause 22 MDIO read/write callbacks, registers the MDIO bus when a PHY address exists, connects the PHY to the PF netdev, adjusts MAC speed/duplex and flow control on PHY link updates, starts/stops/disconnects the PHY, and provides direct firmware PHY register read/write helpers.

## Important APIs And Functions
- `hclge_mac_mdio_config()` validates `hdev->hw.mac.phy_addr`, allocates and registers a devm MDIO bus, sets `read`, `write`, `priv`, `phy_mask`, and stores `mac->phydev`/`mac->mdio_bus`.
- `hclge_mdio_read()` and `hclge_mdio_write()` build `HCLGE_OPC_MDIO_CONFIG` descriptors, encode phy id, register id, start/ST/op fields, check command-disable state, send commands, and return data or errno.
- `hclge_mac_connect_phy()` attaches the stored PHY to the PF netdev using `phy_connect_direct()` with SGMII, limits PHY supported modes to MAC-supported modes, configures Marvell LED flags, and sets default advertising.
- `hclge_mac_adjust_link()` is the PHY link callback. On link-up it calls `hclge_cfg_mac_speed_dup()`, updates requested speed/duplex shadow fields, and reconfigures flow control.
- `hclge_mac_start_phy()`, `hclge_mac_stop_phy()`, and `hclge_mac_disconnect_phy()` wrap PHY lifecycle calls.
- `hclge_read_phy_reg()` and `hclge_write_phy_reg()` use `HCLGE_OPC_PHY_REG` firmware commands for direct register access separate from the Linux MDIO bus callbacks.

## Control Flow
Probe/init calls `hclge_mac_mdio_config()` only when the PF reports a valid PHY address. The registered `mii_bus` makes subsequent PHY library operations call into `hclge_mdio_read/write()`. Client open/connect paths call `hclge_mac_connect_phy()` and later `hclge_mac_start_phy()`. When the PHY reports link changes, `hclge_mac_adjust_link()` updates MAC speed/duplex and flow-control hardware. Stop/remove paths call `hclge_mac_stop_phy()` and `hclge_mac_disconnect_phy()`.

## State And Persistence Behavior
State is kept in `hdev->hw.mac`: `phydev`, `mdio_bus`, requested speed and duplex, supported/advertising masks, and PHY address. MDIO bus allocation is devm-managed, but failed PHY lookup after registration explicitly unregisters the bus. No persistent storage is written; link parameters are shadowed in memory and reprogrammed after PHY events or reset-driven reconnect.

## Dependencies And Integration Points
The file integrates Linux PHY/MDIO APIs (`devm_mdiobus_alloc`, `mdiobus_register`, `mdiobus_get_phy`, `phy_connect_direct`, `phy_start/stop/disconnect`, linkmode helpers) with HNS3 command descriptors. It relies on `hclge_cmd_send()`, bitfield helpers, MAC configuration helpers in PF main code, and flow-control setup from TM/main code. It has a Marvell-specific LED dev flag and assumes `PHY_INTERFACE_MODE_SGMII`.

## Risks And Edge Cases
- `PHY_INEXISTENT` is a driver-local sentinel value of 255; firmware must not use it for a real bus address.
- Only Clause 22 operations are implemented, so Clause 45 PHY requirements would need additional support.
- `hclge_mac_stop_phy()` reads `netdev->phydev`, while other helpers use `hdev->hw.mac.phydev`; mismatch after partial connect/disconnect could matter.
- `hclge_mac_adjust_link()` ignores link-down events, so hardware link-down handling must occur elsewhere.
- Command-disabled state returns `-EBUSY` for MDIO bus operations during reset; PHY library callers must tolerate transient failures.

## Test Signals
Validate probe with no PHY, invalid PHY address, missing PHY after bus registration, successful SGMII PHY attach, autoneg/link changes, Marvell LED flag behavior, ethtool PHY register reads/writes, reset-time `-EBUSY` handling, and MAC speed/duplex/flow-control changes when PHY link comes up.
