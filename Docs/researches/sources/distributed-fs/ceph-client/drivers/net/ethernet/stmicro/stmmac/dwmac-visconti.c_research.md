<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-visconti.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-visconti.c

## Purpose
Toshiba Visconti DWMAC glue that initializes Visconti-specific Ethernet control/clock registers and supplies a speed-dependent TX clock-rate callback.

## Important APIs, Types, And Functions
`struct visconti_eth` stores the MAC register base, `phy_ref_clk`, and device. `visconti_eth_set_clk_tx_rate` programs clock mux/enable/direction for RGMII, RMII, and other modes. `visconti_eth_init_hw` sets PHY interface and releases reset. `visconti_eth_clock_probe/remove` manage clocks. Probe calls `stmmac_dvr_probe` after platform setup.

## Control Flow
Probe obtains STMMAC resources/config, allocates private data, uses the MAC resource as the glue register base, enables `phy_ref_clk`, initializes hardware interface and clocks, forces `dma_cfg->aal = 1`, then calls STMMAC. Clock-rate changes stop internal clocks, program mux selection for speed/interface, enable RX/TX/RMII clocks, and set TX output direction.

## State And Persistence
State is held in Visconti clock/control registers and clock framework state. The driver also disables both `phy_ref_clk` and `priv->plat->stmmac_clk` in its remove helper. No persistent storage exists.

## Dependencies And Integration Points
Depends on STMMAC platform parsing, `stmmac_get_phy_intf_sel`, DWMAC4 definitions, CCF clocks, and OF match `toshiba,visconti-dwmac`.

## Risks
`visconti_eth_init_hw` return value is ignored in probe, so unsupported PHY mode may not abort setup as intended. Clock remove disables `stmmac_clk` in addition to the PHY ref clock, which must align with STMMAC ownership. Speed/interface programming is register-sequence sensitive.

## Test Signals
Probe with GMII/MII/RGMII/RMII modes, unsupported PHY mode handling, 10/100/1000 speed changes, clock enable/disable balance on probe failure and remove, and DMA alignment-sensitive traffic should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-visconti.c -->
