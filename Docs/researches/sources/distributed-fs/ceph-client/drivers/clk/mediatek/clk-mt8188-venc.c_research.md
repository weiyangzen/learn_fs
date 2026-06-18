# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-venc.c

## Purpose
`clk-mt8188-venc.c` registers MT8188 video encoder clock gates.

## Important APIs, Types, And Functions
The driver defines `venc1_cg_regs`, `venc1_clks`, `venc1_desc`, and an OF match for `mediatek,mt8188-vencsys`. Probe/remove are delegated to `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
The common helper registers encoder gates and publishes them as a onecell provider. There is no custom persistence or runtime policy in this file.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are encoder/media drivers and the parent top VENC clock muxes. Risks include gate bit mistakes that appear only when encoding starts. Test signals include video encode workloads, encoder device probe, power-domain transitions, and idle gate disable.
