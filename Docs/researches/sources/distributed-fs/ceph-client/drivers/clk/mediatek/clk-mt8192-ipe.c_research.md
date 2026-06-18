# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-ipe.c

## Purpose
`clk-mt8192-ipe.c` registers MT8192 Image Processing Engine clocks.

## Important APIs, Types, And Functions
The file defines `ipe_cg_regs`, `ipe_clks`, `ipe_desc`, and the `mediatek,mt8192-ipesys` OF match. Runtime operations are `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
The selected descriptor is registered by the simple helper, creating gate clocks and an OF provider. The file has no reset controller or custom persistence.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on IPE clock IDs and top IPE parent clocks. Risks include gate-bit drift and missing clocks for DPE/FD/FE workloads. Test signals include IPE device probe, image workload execution, and suspend/resume.
