# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp1.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vpp1.c

### Purpose
`clk-mt8195-vpp1.c` supplies gates for MT8195 VPPSYS1. It covers SVPP1/2/3 MDP blocks, VPP split/merge, VDO relay links, LARB fake engines, HDMI/DGI paths, display mutex, and 26 MHz split support.

### Important APIs, Types, And Functions
The file defines `vpp1_0_cg_regs`, `vpp1_1_cg_regs`, `GATE_VPP1_0`, `GATE_VPP1_1`, `vpp1_clks`, and `vpp1_desc`. Registration is through a platform ID table and common `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()` helpers.

### Control Flow, State, And Persistence
After platform matching, the common helper registers all gate descriptors against the resource-backed register map and adds a onecell provider. Hardware gate bits in the two VPP1 banks are the only retained state. The driver has no custom sequencing, runtime PM logic, or persistent configuration.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates with MT8195 video/display processing, HDMI receiver paths, DGI paths, and parents `top_vpp`, `hdmirx_p`, `in_dgi`, `top_dgi_out`, and `clk26m`. Risks include accidental gating of relay paths shared with VDO0/VDO1, wrong non-top parent names, and incomplete test coverage for HDMI/DGI-only clocks. Test signals include multi-pipe MDP jobs, display split/merge use, HDMI/DGI input paths, and clk enable-count tracing.
