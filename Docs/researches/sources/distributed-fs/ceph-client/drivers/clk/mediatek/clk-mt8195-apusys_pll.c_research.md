# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-apusys_pll.c

## Purpose
`clk-mt8195-apusys_pll.c` provides MT8195 AI Processing Unit PLL clocks.

## Important APIs, Types, And Functions
It defines `apusys_plls`, `clk_mt8195_apusys_pll_probe()`, `clk_mt8195_apusys_pll_remove()`, and the OF match `mediatek,mt8195-apusys_pll`. Probe uses `mtk_clk_register_plls()` rather than PLLFH registration.

## Control Flow, State, And Persistence
Probe allocates `CLK_APUSYS_PLL_NR_CLK` onecell data, registers APUSYS PLL hardware, publishes the OF provider, and stores driver data. Failure and remove paths unregister PLLs and free clock data after deleting the provider.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are APUSYS/NPU drivers and their power/clock domains. Risks include PLL rate table errors, provider absence causing AI accelerator probe deferral, and missing remove cleanup. Test signals include APUSYS probe, PLL rate requests, clock summary validation, and module remove/reprobe.
