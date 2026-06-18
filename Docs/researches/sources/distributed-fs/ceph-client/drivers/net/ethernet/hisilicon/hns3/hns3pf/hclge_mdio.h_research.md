# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_mdio.h

## Purpose
`hclge_mdio.h` is the small PF MDIO/PHY interface header. It exposes the lifecycle and register-access helpers implemented in `hclge_mdio.c` to PF initialization, client open/close, and diagnostic code.

## Important APIs
- `hclge_mac_mdio_config(struct hclge_dev *hdev)` allocates/registers the MDIO bus and locates the configured PHY.
- `hclge_mac_connect_phy(struct hnae3_handle *handle)` attaches the PHY to the PF netdev and constrains advertised modes.
- `hclge_mac_disconnect_phy(struct hnae3_handle *handle)` detaches the PHY.
- `hclge_mac_start_phy(struct hclge_dev *hdev)` and `hclge_mac_stop_phy(struct hclge_dev *hdev)` control PHY polling/link state.
- `hclge_read_phy_reg()` and `hclge_write_phy_reg()` provide firmware-command register access.

## State, Dependencies, And Integration
The header forward-declares `struct hclge_dev`, includes `hnae3.h` for the handle type, and intentionally hides all MDIO command layout details from callers. It integrates the PF main driver with Linux PHY lifecycle code without exporting the static bus callbacks.

## Risks And Test Signals
The main risk is API sequencing: callers must configure MDIO before connect/start and must tolerate null PHY devices on PHY-less media. Build coverage should catch signature drift, while runtime tests should cover probe/open/stop/remove with both PHY-present and PHY-absent hardware.
