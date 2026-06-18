<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5.c

Purpose: Implements MediaTek MIPI CSI receiver CD-PHY v0.5 support, currently operating CD-PHY-capable blocks only in DPHY mode and supporting a fixed 4-data-plus-1-clock lane mapping.

Important APIs and types: `struct mtk_mipi_cdphy_port` stores device, base, PHY, PHY type, selected mode, and lane count. `enum PHY_TYPE` has DPHY, CPHY, and CDPHY. Key functions are `mtk_mipi_phy_power_on()`, `mtk_mipi_phy_power_off()`, and `mtk_mipi_cdphy_xlate()`.

Control flow: Probe maps registers, reads required `num-lanes`, interprets optional `phy-type` as DPHY or defaults to CDPHY, creates one PHY, and registers custom xlate. Xlate validates phandle arguments: CDPHY requires one argument and only DPHY mode with four lanes; DPHY requires no arguments. Power-on disables CPHY mode for CDPHY hardware, programs lane clock-mode/select mapping across CSIXA and CSIXB, inverts byte clocks, applies CDPHY or DPHY equalizer tuning, sets analog reserve and reset mode fields, then powers bandgap core and LPF. Power-off clears bandgap core/LPF on both halves.

State and persistence: Type, selected mode, and lane count are stored in `port`. Register state persists in both CSIXA and CSIXB banks until power-off or reset.

Dependencies and integration points: Uses generic PHY, DT phy arguments, `dt-bindings/phy/phy.h`, local register definitions, and MediaTek IO helpers. Camera/CSI receiver drivers consume this PHY.

Risks: Only 4D1C DPHY mapping is supported; other valid hardware layouts fail. `mode` is set by xlate, so consumers must request the PHY before power-on. Some raw constants such as `0x90` are not named.

Test signals: MT8365 probe, CDPHY phandle with DPHY argument, invalid argument and lane-count failures, camera stream startup/shutdown, CSIXA/B register readback, and multi-camera concurrent use if instantiated per port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-mipi-csi-0-5.c -->
