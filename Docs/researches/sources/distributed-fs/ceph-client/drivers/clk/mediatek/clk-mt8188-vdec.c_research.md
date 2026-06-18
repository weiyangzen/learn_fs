# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdec.c

## Purpose
`clk-mt8188-vdec.c` provides MT8188 video decoder clocks for SoC and decoder-core domains.

## Important APIs, Types, And Functions
The driver defines three gate register banks, `vdec1_clks`, `vdec2_clks`, and descriptors `vdec1_desc` and `vdec2_desc`. The OF table maps `mediatek,mt8188-vdecsys-soc` and `mediatek,mt8188-vdecsys` to those descriptors.

## Control Flow, State, And Persistence
The simple MediaTek probe registers the matched decoder gate set and publishes it to OF. There is no software persistence beyond clock registrations and hardware gate state.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are V4L2/media decoder drivers. Risks include split-domain ordering, wrong lat/active gate selection, and parent clock mismatches causing decode hangs. Test signals include decoder probe, stream decode start/stop, power-domain transitions, and clock gating during suspend.
