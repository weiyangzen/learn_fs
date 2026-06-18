# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vpp1.c

## Purpose
`clk-mt8188-vpp1.c` provides MT8188 Video Post Processing 1 clocks for the second post-processing/display fabric, including split, merge, scaler, VPP padding, and WPE/VPP links.

## Important APIs, Types, And Functions
It defines two VPP1 gate banks, `vpp1_clks`, `vpp1_desc`, and the `mediatek,mt8188-vppsys1` platform driver using `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()`.

## Control Flow, State, And Persistence
The pdev helper registers the gate table and publishes the OF clock provider. Gate state is persisted only in hardware registers and the CCF while the driver is bound.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are display/video post-processing and WPE-linked paths. Risks include multi-bank gate offset errors and integration mismatches with VDO/VPP parent clocks. Test signals include VPP1 pipeline enablement, WPE/VPP workloads, display suspend/resume, and `clk_summary` gate toggling.
