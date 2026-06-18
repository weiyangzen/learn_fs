# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8365.c

### Purpose
`clk-mt8365.c` is the main MT8365 clock controller driver. It describes topckgen, infracfg, pericfg, and mcucfg clocks including fixed clocks, PLL-derived factors, top muxes, composite audio/misc muxes, dividers, top gates, infra gates, pericfg gate, and MCU bus mux.

### Important APIs, Types, And Functions
Key tables are `top_fixed_clks`, `top_divs`, many parent arrays, `top_misc_muxes`, `top_muxes`, `mcu_muxes`, `top_adj_divs`, `top_clk_gates`, `ifr_clks`, `peri_clks`, and descriptors `topck_desc`, `infra_desc`, `peri_desc`, `mcu_desc`. It uses `mtk_mux`, `mtk_composite`, `mtk_gate`, `mtk_clk_divider`, and a shared spinlock.

### Control Flow, State, And Persistence
`mtk_clk_simple_probe()` selects a descriptor from OF compatibles `mt8365-topckgen`, `mt8365-infracfg`, `mt8365-pericfg`, or `mt8365-mcucfg`, then registers the relevant tables. Hardware mux, divider, and gate registers retain current clock configuration; the driver stores no nonvolatile data.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APMIXED PLL names (`mainpll`, `univ_en`, `apll*`, etc.), syscon/regmap-ready clock infrastructure, peripheral drivers, and MT8365 bindings. Risks include large parent-order tables, critical flags on AXI/DXCC/SPM/MCU clocks, duplicate-looking divider lines, and cross-provider parent resolution. Test signals include complete boot without unresolved parents, UART/storage/USB/audio/display/camera/APU probes, CPU bus rate behavior, and clk tree validation.
