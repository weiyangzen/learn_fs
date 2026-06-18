<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-img.c

Purpose: This driver registers MT8183 image subsystem gates.

Important APIs, types, and functions: `img_cg_regs`, `GATE_IMG`, `img_clks`, and `img_desc` describe the image gate provider matched by `mediatek,mt8183-imgsys`.

Control flow: `mtk_clk_simple_probe` registers all image gates and publishes the OF provider. Image/ISP/MDP-related consumers enable gates through the common clock framework.

State and persistence behavior: The gate register bits are volatile; provider data is runtime-only.

Dependencies and integration points: It depends on MT8183 clock bindings, MediaTek gate helpers, top-level image parent clocks, and image processing consumers.

Risks and edge cases: Gate bits usually protect memory-facing image blocks, so bad gating can manifest as DMA/IOMMU faults. Runtime PM must keep gates balanced.

Test signals: Image pipeline operation, clk summary gate changes during use, suspend/resume, and driver unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-img.c -->
