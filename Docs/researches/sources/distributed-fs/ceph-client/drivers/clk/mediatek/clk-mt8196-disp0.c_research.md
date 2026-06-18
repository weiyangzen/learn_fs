# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp0.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-disp0.c

### Purpose
`clk-mt8196-disp0.c` describes the MT8196 primary display clock gate domain. It covers display configuration, mutex, AAL, C3D, color/correction, CHIST, dither, DLI/DLO async, gamma, MDP, postmask, RSZ, SPR, WDMA, Y2R, SMI, and fake-engine clocks.

### Important APIs, Types, And Functions
The file uses normal gate macros (`GATE_MM0`, `GATE_MM1`) and hardware-voter macros (`GATE_HWV_MM0`, `GATE_HWV_MM1`). HWV gates carry `hwv_regs` pointing to done/set/clear registers and use `mtk_clk_gate_hwv_ops_setclr`; non-HWV gates use `mtk_clk_gate_ops_setclr`. `mm_mcd` is registered through `mtk_clk_pdev_probe()`.

### Control Flow, State, And Persistence
The platform probe registers the table as a provider. Gate operations may either write local CG registers or request hardware-voter operations depending on each descriptor. Runtime state is split between display CG registers and HWV status registers; no software state is persisted.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `disp`, MT8196 IDs, MediaTek HWV gate support, and display/MDP consumers. Risks are wrong HWV register offsets, parent-enable semantics not matching hardware power dependencies, and display path hangs if async or SMI clocks are gated unexpectedly. Test signals include display pipeline boot, HWV gate enable/disable completion, clk summary parent enables, DRM modeset, and runtime suspend.
