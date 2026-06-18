# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516.c

### Purpose
`clk-mt8516.c` is the main MT8516 top and infra clock controller. It defines fixed clocks, PLL-derived factors, top muxes, infra muxes, audio dividers, top gates, and descriptors for topckgen and infracfg.

### Important APIs, Types, And Functions
Important data includes `fixed_clks`, `top_divs`, large parent arrays, `top_muxes`, `ifr_muxes`, `top_adj_divs`, `top_clks`, `topck_desc`, and `infra_desc`. It uses `mtk_composite`, `mtk_clk_divider`, `mtk_gate`, a shared `mt8516_clk_lock`, and the common MediaTek simple clock probe.

### Control Flow, State, And Persistence
OF matching selects `mediatek,mt8516-topckgen` or `mediatek,mt8516-infracfg`. The common helper registers the selected table sets and exposes the provider. Top muxes and gates are init-data heavy but registered into the clock framework; hardware registers hold mux/divider/gate state. No nonvolatile state is stored.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APMIXED PLL names, `clk26m`, many peripheral consumers, and MT8516 binding IDs. Risks include very sparse parent arrays with `clk_null`, no-setclr/inverted gate variations, audio divider chains, and parent name compatibility with old DTs. Test signals include boot provider resolution, UART/I2C/MSDC/USB/Ethernet/audio probes, audio divider rate checks, NAND/NFI paths, and clk tree dumps.
