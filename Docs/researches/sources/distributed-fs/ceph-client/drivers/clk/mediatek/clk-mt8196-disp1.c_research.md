# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp1.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp1.c

### Purpose
`clk-mt8196-disp1.c` registers the MT8196 secondary display clock domain. It gates dispsys1 config, display mutex, DLI/DLO async paths, relay, DP/DSI/DVO, DSC, GDMA, merge, ODDMR, postalign, dither, splitters, WDMA, SMI LARB, module clocks, and 26 MHz support.

### Important APIs, Types, And Functions
Two clock-gate banks are modeled by `mm10_cg_regs` and `mm11_cg_regs`, with corresponding HWV register banks. `GATE_HWV_MM10` and `GATE_HWV_MM11` use `mtk_clk_gate_hwv_ops_setclr`; normal macros use `mtk_clk_gate_ops_setclr`. The platform ID table passes `mm1_mcd` into `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The common platform probe creates the clock provider from the descriptor. Runtime clock changes are table-driven and write either HWV or direct CG registers, with `CLK_OPS_PARENT_ENABLE` on all gates. State persists only as hardware register state across the display power domain.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parents `disp`, `clk26m`, `dp0`, and `dp1`, plus DRM display consumers. Risks include unusual clock names such as `mm1_CLK0` and `mm1_DP_CLK`, HWV completion timeouts, and display-output-specific clocks being untested. Test signals include secondary display/DSI/DP paths, clock provider binding by platform name, HWV status observation, and suspend/resume display tests.
