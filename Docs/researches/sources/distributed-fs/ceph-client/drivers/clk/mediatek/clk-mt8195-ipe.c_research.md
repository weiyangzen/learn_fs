# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-ipe.c

## Purpose
`clk-mt8195-ipe.c` registers MT8195 Image Processing Engine clocks.

## Important APIs, Types, And Functions
The file defines `ipe_cg_regs`, `ipe_clks`, `ipe_desc`, and OF compatible `mediatek,mt8195-ipesys`. It uses the common simple probe/remove helpers.

## Control Flow, State, And Persistence
The matched descriptor is registered by `mtk_clk_simple_probe()`, creating gate clocks and an OF provider. There is no custom reset or policy state.

## Dependencies, Integration Points, Risks, And Test Signals
Integration consumers are MT8195 IPE imaging blocks. Risks include gate bit errors and missing parent clocks that only surface under imaging workloads. Test signals include IPE probe, image-processing execution, runtime PM, and suspend/resume.
