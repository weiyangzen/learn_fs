# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp0.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp0.c

### Purpose
`clk-mt8195-vpp0.c` implements the first MT8195 video processing pipe clock provider. It gates MDP, warp async, mutex, VPP relay, SMI, GALS bridge, HDR/TDSHP/color/OVL, and warp relay clocks.

### Important APIs, Types, And Functions
Important objects are three gate-register banks, the `GATE_VPP0_*` macros, `vpp0_clks`, `vpp0_desc`, and a platform driver wired to `mtk_clk_pdev_probe()`. All gates use non-inverted set/clear operations through `mtk_clk_gate_ops_setclr`.

### Control Flow, State, And Persistence
The probe path is the common MediaTek platform descriptor path: match platform ID, map registers, register gate clocks, and expose the provider. Runtime state is only hardware clock-gate bits across VPP0_0, VPP0_1, and VPP0_2 banks. No persistent data is written.

### Dependencies, Integration Points, Risks, And Test Signals
The provider depends on parent clocks `top_vpp` and `top_wpe_vpp`, MT8195 binding IDs, and display/MDP/warp consumers. Risks include incorrect cross-pipe relay gating, SMI/IOMMU clock omissions leading to bus faults, and parent dependency changes in topckgen. Test signals include MDP and display processing tests, warp-engine workflows, SMI/LARB activity, clock debugfs enables, and suspend/resume.
