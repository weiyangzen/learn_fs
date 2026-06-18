# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-gmii-sel.c

## Purpose
Generic PHY wrapper for TI CPSW Ethernet interface mode selection. Each PHY maps to a CPSW port and writes SoC control-module fields for MII, RMII, RGMII variants, SGMII, QSGMII, or USXGMII.

## APIs, Flow, And State
Controller state is `struct phy_gmii_sel_priv`; per-port state is `struct phy_gmii_sel_phy_priv`; SoC differences live in `struct phy_gmii_sel_soc_data`. Probe selects compatible-specific data, reads optional QSGMII main ports, gets parent syscon or MMIO regmap, allocates per-port regmap fields, creates one PHY per port, and registers xlate. `phy_gmii_sel_of_xlate()` validates port cells and records RMII external clock when required. `phy_gmii_sel_mode()` validates `PHY_MODE_ETHERNET`, maps Linux `phy_interface_t` submodes to hardware values, writes mode/RGMII delay/RMII clock fields, and stores `phy_if_mode` for resume.

## Dependencies And Integration
Depends on generic PHY, regmap-field, syscon/MMIO fallback, OF, and Ethernet PHY interface mode constants. CPSW consumers call `.set_mode()` through PHY handles.

## Risks And Tests
Resume only replays nonzero `phy_if_mode`, so enum-zero modes may be skipped. A debug print can reference a missing second xlate arg on non-RMII-clock SoCs. Test every SoC table, RMII external clock cells, QSGMII main/sub mapping, unsupported mode rejection, fixed-delay RGMII rejection, and noirq resume restore.
