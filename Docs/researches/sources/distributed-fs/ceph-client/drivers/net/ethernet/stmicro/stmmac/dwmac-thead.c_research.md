<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-thead.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-thead.c

## Purpose
T-HEAD TH1520 DWMAC platform glue that controls APB-side GMAC interface, clock direction, PLL divider, and delay registers around generic STMMAC platform probing.

## Important APIs, Types, And Functions
`struct thead_dwmac` stores the STMMAC platform data, APB register mapping, and device pointer. `thead_dwmac_set_phy_if`, `thead_dwmac_set_txclk_dir`, `thead_dwmac_enable_clk`, and `thead_set_clk_tx_rate` program glue registers. `thead_dwmac_init` is the platform init callback and `thead_dwmac_probe` wires resources.

## Control Flow
Probe gets STMMAC resources/config, optionally enables the APB clock with a warning for old DTs, maps APB register resource 1, sets `bsp_priv`, `set_clk_tx_rate`, and `init`, then calls `devm_stmmac_pltfr_probe`. Init validates MII/RGMII modes, sets interface and TX clock direction, clears RX/TX delay fields to zero, and enables clocks. RGMII speed changes compute divider from `stmmac_clk` and `rgmii_clock(speed)`.

## State And Persistence
Persistent device state is APB register programming and devm-managed clock/map lifetime. The PLL divider and clock enables persist until reset or driver removal. There is no persistent storage.

## Dependencies And Integration Points
Uses STMMAC platform config, `rgmii_clock`, OF/platform resources, CCF, and APB glue registers. It supports MII and RGMII-family modes only.

## Risks
Divider programming assumes `stmmac_clk` is an exact multiple of target RGMII clock; non-divisible rates fail link speed changes. APB clock may be absent for old DTs, leaving speed changes potentially fragile. RX/TX delay fields are hard-coded to zero, so board timing relies on PHY/interface delays.

## Test Signals
TH1520 probe with new and old DTs, MII vs RGMII register values, 10/100/1000 RGMII rate changes, invalid clock-rate rejection, and link stability after speed renegotiation are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-thead.c -->
