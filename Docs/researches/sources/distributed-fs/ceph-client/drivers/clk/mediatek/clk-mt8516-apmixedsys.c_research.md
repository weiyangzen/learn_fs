# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-apmixedsys.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8516-apmixedsys.c

### Purpose
`clk-mt8516-apmixedsys.c` registers MT8516 APMIXED PLLs: ARMPLL, MAINPLL, UNIVPLL, MMPLL, APLL1, and APLL2. These are root inputs for the MT8516 top clock tree and audio/multimedia subsystems.

### Important APIs, Types, And Functions
The file defines `PLL_B`, `PLL`, `mmpll_div_table`, `plls`, and `clk_mt8516_apmixed_probe()`. Probe uses `devm_platform_ioremap_resource()`, `mtk_devm_alloc_clk_data()`, `mtk_clk_register_plls()`, and `of_clk_add_hw_provider()`. The driver is registered using `builtin_platform_driver()`.

### Control Flow, State, And Persistence
As a built-in driver, probe maps registers early, allocates clock data, registers PLLs, and publishes the provider. On provider registration failure, it unregisters PLLs. PLL control, power, post-divider, tuner, and PCW fields are stored in hardware registers; no software persistence is kept.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include MT8516 clock bindings, topckgen consumers, `clk-pll.h`, OF, and early platform probing. Risks include PLL max frequency limits, reset-bar bit modeling, MMPLL divider table accuracy, and lack of explicit remove cleanup. Test signals include topckgen parent resolution, audio PLL rate generation, CPU/main PLL rates, boot ordering, and forced error-path tests.
