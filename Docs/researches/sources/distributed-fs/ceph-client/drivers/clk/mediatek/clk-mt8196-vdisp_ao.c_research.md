# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdisp_ao.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-vdisp_ao.c

### Purpose
`clk-mt8196-vdisp_ao.c` registers a small MT8196 always-on display clock provider for VDISP AO configuration, DPC, and SMI sub-SOMM0 clocks.

### Important APIs, Types, And Functions
It defines one direct gate bank, one HWV bank, `GATE_MM_AO_V`, `GATE_HWV_MM_V`, `mm_v_clks`, and `mm_v_mcd`. The SMI sub-SOMM0 clock is marked `CLK_IS_CRITICAL`; HWV clocks use `mtk_clk_gate_hwv_ops_setclr`. The platform driver uses `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform provider registers three clocks from the descriptor. DPC and config gates use hardware-voter operations, while the SMI sub-clock uses direct set/clear and is kept critical. State resides in CG/HWV registers only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `disp`, display power management, and SMI/display consumers. Risks include critical-clock misuse, HWV offset errors, and provider matching through OF data with a platform-probe helper. Test signals include display boot with unused-clock cleanup enabled, DPC activity, clk critical flag visibility, and suspend/resume.
