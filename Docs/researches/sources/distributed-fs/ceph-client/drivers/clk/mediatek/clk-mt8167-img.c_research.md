<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-img.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-img.c

Purpose: This file registers MT8167 image subsystem gates for the image LARB, SMI, and camera/image processing clocks.

Important APIs, types, and functions: `img_cg_regs` describes the set/clear/status offsets; `GATE_IMG` creates `struct mtk_gate` entries; `img_desc` is selected by `mediatek,mt8167-imgsys`; probe/remove use MediaTek simple helpers.

Control flow: The platform driver maps the imgsys clock-gate registers, registers all gates in `img_clks`, and exposes them as an OF provider. Camera/image consumers request gates by MT8167 binding IDs.

State and persistence behavior: State is limited to volatile gate bits and the runtime clock-provider data. There is no software persistence.

Dependencies and integration points: It depends on common MediaTek clock gate code, `dt-bindings/clock/mt8167-clk.h`, and topckgen parents for the image domain. It integrates with image sensor/camera and memory-interface drivers.

Risks and edge cases: A wrong gate bit can block memory access for the image subsystem. Since gates share one register set, polarity and set/clear semantics are important.

Test signals: Image/camera pipeline probe, LARB/SMI access with clocks enabled, clk summary transitions during runtime PM, and clean provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-img.c -->
