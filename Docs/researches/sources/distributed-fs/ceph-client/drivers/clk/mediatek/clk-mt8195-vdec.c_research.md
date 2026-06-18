# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdec.c

## Purpose
`clk-mt8195-vdec.c` registers MT8195 video decoder clocks for primary decoder, core1, and decoder SoC domains.

## Important APIs, Types, And Functions
The file defines three decoder gate register banks, gate arrays `vdec_clks`, `vdec_core1_clks`, and `vdec_soc_clks`, descriptors for each, and OF matches `mediatek,mt8195-vdecsys`, `vdecsys_core1`, and `vdecsys_soc`.

## Control Flow, State, And Persistence
The simple helper registers the matched decoder-domain gates and publishes an OF provider. State persists as CCF clock registrations and gate bits until remove.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are MT8195 media decoder drivers and power-domain code. Risks include split-domain gate mistakes, decode hangs under core1 workloads, and parent mismatch with top VDEC muxes. Test signals include V4L2 decode on each core/domain, power-domain cycling, idle gating, and suspend/resume.
