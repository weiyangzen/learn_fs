# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen2.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-topckgen2.c

### Purpose
`clk-mt8196-topckgen2.c` implements the MT8196 GP2 top clock generator for multimedia-heavy roots: sensor interfaces, image/IPE/camera/DPE, VDEC/VENC, CCU, DVO/DP, display, MDP, MMINFRA, MMUP, and MMINFRA_AO.

### Important APIs, Types, And Functions
The main data is `top_divs`, multimedia parent arrays, `top_muxes`, and `topck_desc`. It uses GP2 register offsets (`CKSYS2_CLK_CFG_*`), fenced mux macros, and HWV mux-gate macros using `MM_HWV_CG_*` and `MM_HWV_MUX_UPDATE_31_0` infrastructure. Registration is through `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
The common probe registers fixed factors and muxes for `mediatek,mt8196-topckgen-gp2`. Hardware state lives in CKSYS2 mux registers, set/clear registers, update bits, fence status, and multimedia HWV done registers. No custom state is held in the driver.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APMIXED2 PLLs (`mainpll2`, `univpll2`, `mmpll2`, `imgpll`, `tvdpll*`), display/media consumers, and HWV support. Risks include multimedia parent-order mistakes, fractional TVDPLL factors, fence bit mapping, and display/camera paths failing only under high-rate configurations. Test signals include camera/video/display probes, DP/DVO output rates, VDEC/VENC throughput tests, clk summary parent selection, and fence timeout logs.
