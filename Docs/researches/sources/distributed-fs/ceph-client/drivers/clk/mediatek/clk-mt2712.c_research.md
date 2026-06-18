<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712.c

### Purpose
`clk-mt2712.c` is the main MT2712 top/infrastructure/peripheral/MCU clock provider. It models fixed roots, PLL factors, a large top mux table, MCU CPU/bus muxes, audio dividers/gates, infra gates, peri gates, and reset descriptors.

### Important APIs, Types, And Functions
Important tables include `top_fixed_clks[]`, `top_divs[]`, extensive parent arrays, `top_muxes[]`, `mcu_muxes[]`, `top_adj_divs[]`, `top_clks[]`, `infra_clks[]`, `peri_clks[]`, `clk_rst_desc[]`, and descriptors `topck_desc`, `mcu_desc`, `infra_desc`, `peri_desc`. The driver uses `mtk_clk_simple_probe()` with match data for `mediatek,mt2712-infracfg`, `-mcucfg`, `-pericfg`, and `-topckgen`.

### Control Flow, State, And Persistence
Probe is descriptor-driven: the common simple probe allocates clock data, maps resources, registers fixed/factor/composite/divider/gate groups as listed in the matching descriptor, registers reset controllers for infra/peri, and publishes the onecell provider. Runtime state persists in topckgen mux/divider/gate registers, MCU mux registers, infra/peri gate registers, and reset banks.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MT2712 DT bindings, `clk-mtk`, `clk-gate`, reset helpers, and consumers across CPU, display, storage, audio, Ethernet, and peripheral subsystems. Risks include descriptor typos, critical-clock flag mistakes, unusual duplicated/extra braces visible in the source, parent names that must match the APMIXED PLL provider, and reset bank map errors. Test signals include full MT2712 boot, CPU cluster mux operation, storage/audio/display/Ethernet probe, reset controller users, and `clk_summary` topology validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2712.c -->
