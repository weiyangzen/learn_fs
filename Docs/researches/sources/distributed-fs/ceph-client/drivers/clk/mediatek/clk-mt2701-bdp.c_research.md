<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-bdp.c -->
## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-bdp.c

### Purpose
This file provides MT2701 BDPSYS gate clocks for video/display processing blocks such as BRZ, BLS, WDMA, and TVD-related paths.

### Important APIs, Types, And Functions
It defines `bdp0_cg_regs`, `bdp1_cg_regs`, `GATE_BDP0/1`, the `bdp_clks[]` descriptor table, `bdp_desc`, and a `module_platform_driver()` using `mtk_clk_simple_probe`.

### Control Flow, State, And Persistence
On a `mediatek,mt2701-bdpsys` platform device, the simple probe registers all gates into the DT onecell provider. Runtime enable/disable uses set/clear/status register banks; no additional persistent software state is kept.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on DT binding IDs, `clk-gate`, `clk-mtk`, and consumers in display/video pipelines. Risks are wrong parent clocks, swapped gate banks, and missing consumers causing display/video failures. Test signals are successful BDPSYS probe, enabling display/video consumers, and clock summary transitions during multimedia use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt2701-bdp.c -->
