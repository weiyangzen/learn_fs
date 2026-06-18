<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765.c

### Purpose
`clk-mt6765.c` is the main MT6765 clock driver. It provides APMIXED PLLs and 26 MHz gates, topckgen fixed/factor/mux/gate clocks, and infracfg gates.

### Important APIs, Types, And Functions
Important state includes global `cksys_base` and `apmixed_base`, register macros derived from them, `fixed_clks[]`, `top_divs[]`, parent arrays, `top_muxes[]`, `top_clks[]`, `ifr_clks[]`, `apmixed_clks[]`, `plls[]`, and probe functions `clk_mt6765_apmixed_probe()`, `clk_mt6765_top_probe()`, `clk_mt6765_ifr_probe()`, and dispatcher `clk_mt6765_probe()`.

### Control Flow, State, And Persistence
The driver registers at `arch_initcall()`. Match data dispatches by compatible: APMIXED maps PLL registers, registers PLLs and extra 26 MHz gates, stores `apmixed_base`, and programs AP_PLL/PLLON hardware mode bits; TOP registers fixed/factor/mux/gate clocks, stores `cksys_base`, and sets SCP configuration bits; IFR registers infra gates. Clock state persists in top mux/gate registers, infra gate banks, APMIXED PLL/gate registers, and two global base pointers.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `clk-mux`, `clk-gate`, `clk-pll`, DT bindings, and consumers across display, camera, audio, storage, USB, modem, and infra peripherals. Risks include global base pointer ordering, raw register writes with magic masks, no reset descriptors, parent name drift, and source typos/extra braces visible in table regions. Test signals include full MT6765 boot, clock provider registration for all three compatibles, storage/audio/display/camera probe, PLL rate checks, and `clk_summary` verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6765.c -->
