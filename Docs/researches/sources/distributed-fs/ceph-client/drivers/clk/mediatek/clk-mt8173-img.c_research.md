<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-img.c

Purpose: This file exposes MT8173 image subsystem clock gates.

Important APIs, types, and functions: `img_cg_regs` describes the image gate register bank; `GATE_IMG` creates `img_clks`; `img_desc` is attached to `mediatek,mt8173-imgsys`. The driver uses `mtk_clk_simple_probe/remove`.

Control flow: The OF platform driver registers image gates when the imgsys node probes. Consumers then enable the LARB/SMI and image processing gates by DT clock ID.

State and persistence behavior: The only persistent-at-runtime state is MMIO gate bits and common clock framework registration. Removal unregisters provider state.

Dependencies and integration points: It depends on MT8173 clock bindings, common MediaTek gate helpers, parent clocks from topckgen, and image/camera/media drivers.

Risks and edge cases: The driver name and description mention vdecsys even though it binds imgsys, so diagnostics can be confusing. Gate bit and parent mismatches can break image DMA paths.

Test signals: Imgsys node binding, camera/image pipeline operation, LARB clock enable sequencing, clk summary gate toggles, and module unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8173-img.c -->
