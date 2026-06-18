<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-img.c

Purpose: This provider registers MT8186 image subsystem clocks for imgsys1 and imgsys2.

Important APIs, types, and functions: `img_cg_regs` backs both `img1_clks` and `img2_clks`; `img1_desc` and `img2_desc` are selected by `mediatek,mt8186-imgsys1` and `mediatek,mt8186-imgsys2`.

Control flow: Simple probe picks the descriptor by compatible string, registers the image gates, and publishes the provider for image/ISP consumers.

State and persistence behavior: Gate state is volatile MMIO state; provider data is runtime-only.

Dependencies and integration points: It depends on MT8186 bindings, common gate helpers, top-level image parents, image processing drivers, power domains, and memory fabric clocks.

Risks and edge cases: Two image subsystems share code but have distinct clock IDs. A descriptor mismatch can expose the wrong clocks to a DT node.

Test signals: Both imgsys nodes bind, image processing workloads run on both domains, clk summary gate toggling, runtime PM, and unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-img.c -->
