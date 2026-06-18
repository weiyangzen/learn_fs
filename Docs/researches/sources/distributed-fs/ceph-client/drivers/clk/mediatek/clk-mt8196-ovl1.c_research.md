# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl1.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-ovl1.c

### Purpose
`clk-mt8196-ovl1.c` mirrors the first overlay provider for MT8196 overlay system 1. It gates the ovl1 config, fake engines, mutex, EXDMA, blenders, output processors, MDP RSZ, WDMA, UFBC, MDP RDMA, BWM, DLI/DLO links, relay, inline rotation, and SMI clocks.

### Important APIs, Types, And Functions
The key objects are `ovl10_cg_regs`, `ovl11_cg_regs`, HWV registers, `GATE_HWV_OVL10`, `GATE_HWV_OVL11`, `ovl1_clks`, and `ovl1_mcd`. The platform driver uses `mtk_clk_pdev_probe()` and `mtk_clk_pdev_remove()`.

### Control Flow, State, And Persistence
Common probe registers all HWV gates and exposes the clock provider. All enable/disable operations are table-driven through hardware-voter set/clear ops. The only durable state is hardware gate status; no runtime PM or custom software state appears in this file.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include parent `disp`, overlay pipeline consumers, and the HWV gate implementation. Risks are table drift from ovl0, incorrect duplicate clock naming, and missed SMI/relay dependencies for secondary display paths. Test signals include ovl1 display composition, multi-display overlay use, HWV done-register checks, and provider unbind/rebind.
