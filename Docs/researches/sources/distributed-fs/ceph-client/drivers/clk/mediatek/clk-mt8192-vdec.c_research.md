# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-vdec.c

## Purpose
`clk-mt8192-vdec.c` provides MT8192 video decoder clocks for core and SoC decoder domains.

## Important APIs, Types, And Functions
The file defines three decoder gate banks, `vdec_clks`, `vdec_soc_clks`, descriptors `vdec_desc` and `vdec_soc_desc`, and OF matches `mediatek,mt8192-vdecsys` and `mediatek,mt8192-vdecsys_soc`.

## Control Flow, State, And Persistence
The simple probe registers the matched decoder-domain gates and publishes an OF provider. State is limited to the common clock registrations and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are media decoder drivers and power-domain code. Risks include split core/SOC domain gate mistakes causing decode hangs. Test signals include V4L2 decode, power-domain cycling, and clock disable on decoder idle.
