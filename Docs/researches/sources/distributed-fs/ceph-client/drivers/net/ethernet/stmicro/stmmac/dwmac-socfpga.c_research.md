<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-socfpga.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-socfpga.c

## Purpose
`dwmac-socfpga.c` is the Altera/Intel SoCFPGA stmmac glue layer. It programs system-manager PHY mode bits under reset, supports optional FPGA EMAC splitter and GMII-to-SGMII adapter blocks, creates a Lynx PCS over an MMIO-backed MDIO regmap, and adds Agilex5 XGMAC/PTP cross-timestamp support.

## Important APIs, Types, and Functions
- `struct socfpga_dwmac_ops` selects Gen5, Gen10, or Agilex5 PHY-mode and platform setup behavior.
- `struct socfpga_dwmac` stores sysmgr offset/shift, stmmac platform data, resets, optional splitter/TSE PCS/SGMII adapter mappings, F2H PTP clock flag, and ops.
- `socfpga_dwmac_parse_data()` reads `altr,sysmgr-syscon`, optional splitter and converter phandles, and maps auxiliary resources.
- `socfpga_gen5_set_phy_mode()` and `socfpga_gen10_set_phy_mode()` assert resets, update sysmgr PHY/PTP/F2H bits, then deassert resets.
- `socfpga_dwmac_fix_mac_speed()` updates splitter speed and toggles SGMII adapter enable around changes.
- `socfpga_dwmac_pcs_init()` creates a regmap MDIO bus and Lynx PCS when TSE PCS MMIO is present.
- `smtg_crosststamp()` implements Agilex5 hardware cross-timestamping using internal snapshot and SMTG MDIO time.

## Control Flow
Probe selects ops, gets stmmac resources and DT config, allocates private state, obtains optional OCP reset and deasserts it, parses sysmgr/auxiliary data, stores the stmmac reset handle for later mode changes, assigns stmmac fix-speed/init/PCS callbacks, applies variant platform setup, and calls `devm_stmmac_pltfr_probe()`. Stmmac init calls the selected PHY-mode writer; link changes update splitter/adapter state.

## State and Persistence
Private state is devm-managed. Persistent hardware state includes sysmgr PHY selection, FPGA interface enable bits, PTP reference clock selection, reset line state, splitter speed, SGMII adapter enable, PCS registers, and PTP auxiliary timestamp configuration. Cross-timestamping uses stmmac locks and MMIO/MDIO reads but no storage.

## Dependencies and Integration Points
The driver depends on Altera sysmgr regmap helpers, reset controls, stmmac GMAC/XGMAC/PTP internals, MDIO regmap, Lynx PCS, phylink, and ARM architectural counter IDs. Compatible strings are `altr,socfpga-stmmac`, `altr,socfpga-stmmac-a10-s10`, and `altr,socfpga-stmmac-agilex5`.

## Risks and Edge Cases
- The driver must own resets while changing PHY mode; reset sequencing errors can leave the MAC sampling stale mode bits.
- Splitter presence forces MAC-side GMII/MII selection even when the external PHY mode differs.
- SGMII adapter resources are optional and identified by `reg-names`; missing names silently skip related support.
- Cross-timestamping rejects concurrent external snapshot use and assumes SMTG MDIO reads succeed.
- Agilex5 enables TBS only on queues 6 and 7 for 7/8 queue configurations.

## Test Signals
Test Gen5 and Gen10 sysmgr writes for RGMII/RMII/SGMII/1000BASE-X, splitter speed changes at 10/100/1000, SGMII adapter toggling, PCS creation over TSE control port, reset assert/deassert ordering, Agilex5 XGMAC setup, TSO/TBS queue flags, and PTP cross-timestamp ioctl behavior including `-EBUSY` when external snapshots are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-socfpga.c -->
