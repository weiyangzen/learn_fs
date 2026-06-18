<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mm.c

Purpose: This is the MT8167 multimedia system gate provider for display, SMI/LARB, MDP, DPI/DSI, and related MM clocks.

Important APIs, types, and functions: `mm0_cg_regs` and `mm1_cg_regs` describe two gate banks; `GATE_MM0` and `GATE_MM1` populate `mm_clks`; `mm_desc` groups the gates. Unlike OF-matched simple drivers, it uses a platform device ID `clk-mt8167-mm` and `mtk_clk_pdev_probe/remove`.

Control flow: A parent platform/MFD device instantiates `clk-mt8167-mm`; the pdev probe fetches `mm_desc` from driver data, registers all MM gate clocks, and provides them to consumers.

State and persistence behavior: Gate state is volatile MM system register state. The platform-device provider data is runtime-only and removed by `mtk_clk_pdev_remove`.

Dependencies and integration points: It depends on MediaTek common pdev clock helpers, MT8167 clock IDs, topckgen MM parents, and display/media consumers. The platform-device integration means DT matching may happen in a parent syscon/MFD path rather than directly here.

Risks and edge cases: Two register banks increase the chance of bit-offset mistakes. Display and memory paths are sensitive to gating order with power domains and larb/IOMMU setup.

Test signals: Display pipeline startup, MDP operations, LARB/SMI consumers, pdev creation from the parent device, runtime PM gate toggling, and module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-mm.c -->
