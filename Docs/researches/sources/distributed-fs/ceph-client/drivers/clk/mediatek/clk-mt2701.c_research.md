<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701.c

### Purpose
`clk-mt2701.c` is the main MT2701 clock provider. It covers topckgen fixed clocks, PLL-derived factors, top muxes/dividers/gates, infra CPU mux and gates, pericfg gates/muxes/resets, and APMIXED PLLs.

### Important APIs, Types, And Functions
Important data includes `top_fixed_clks[]`, `top_fixed_divs[]`, many parent arrays, `cpu_muxes[]`, `top_muxes[]`, `top_adj_divs[]`, `top_clks[]`, `infra_clks[]`, `infra_fixed_divs[]`, `peri_clks[]`, `peri_muxs[]`, `apmixed_plls[]`, and `apmixed_fixed_divs[]`. Probe dispatch functions are `mtk_topckgen_init()`, `mtk_infrasys_init_early()`, `mtk_infrasys_init()`, `mtk_pericfg_init()`, `mtk_apmixedsys_init()`, and `clk_mt2701_probe()`.

### Control Flow, State, And Persistence
The driver registers at `arch_initcall()` so core clocks appear early. `mtk_topckgen_init()` maps topckgen, allocates clock data, registers fixed/factor/composite/divider/gate clocks, and publishes an OF provider. Infrasys has an early `CLK_OF_DECLARE_DRIVER` path to register fixed factors and CPU muxes with placeholder slots, then the platform probe completes gates and reset registration. Pericfg registers peripheral gates, UART muxes, and resets. APMIXED registers PLLs and one HDMI reference factor. Clock state persists in hardware mux, divider, gate, PLL, and reset registers plus the global `infra_clk_data` pointer.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on DT bindings, `clk-mtk`, `clk-pll`, `clk-gate`, `clk-cpumux`, reset helpers, and CCF provider registration. Risks include early/late infrasys ordering, duplicated descriptor lines, unchecked registration helper return values, critical clock flags on AXI/MEM/RTC, PLL parameter mistakes, and reset-bank errors. Test signals are full MT2701 boot, CPU parent switching, peripheral probe coverage, reset controller users, clock debugfs hierarchy, and failure-injection of provider registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701.c -->
