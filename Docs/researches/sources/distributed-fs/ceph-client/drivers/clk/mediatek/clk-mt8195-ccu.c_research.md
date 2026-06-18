# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-ccu.c

## Purpose
`clk-mt8195-ccu.c` registers MT8195 camera control unit clocks.

## Important APIs, Types, And Functions
It defines `ccu_cg_regs`, `ccu_clks`, `ccu_desc`, and OF compatible `mediatek,mt8195-ccusys`. Runtime operations are `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe registers CCU gates and publishes the OF provider for camera-control consumers. No extra state is stored beyond the common clock provider.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies are CCU DT nodes, MT8195 clock IDs, and top CCU parents. Risks include camera firmware/control failures if the CCU clock gate is wrong. Test signals include CCU consumer clock lookup, camera pipeline startup, and runtime suspend/resume.
