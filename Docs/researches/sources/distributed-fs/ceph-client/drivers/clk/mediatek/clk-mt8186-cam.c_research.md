<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-cam.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-cam.c

Purpose: This driver registers MT8186 camera clock gates for the main camera system and two raw camera subsystems.

Important APIs, types, and functions: `cam_cg_regs` backs `cam_clks`, `cam_rawa_clks`, and `cam_rawb_clks`. Three descriptors, `cam_desc`, `cam_rawa_desc`, and `cam_rawb_desc`, are selected by compatibles `mediatek,mt8186-camsys`, `mediatek,mt8186-camsys_rawa`, and `mediatek,mt8186-camsys_rawb`.

Control flow: Simple probe registers the descriptor selected by OF match data. Each camera node exposes its own gate set to camera pipeline consumers.

State and persistence behavior: Gate bits are volatile camera subsystem registers. Provider state is runtime-only.

Dependencies and integration points: It depends on MT8186 clock IDs, common MediaTek gate helpers, topckgen camera parents, camera drivers, raw sensor paths, power domains, and memory/LARB clocks.

Risks and edge cases: Multiple compatibles share one register layout but expose different IDs; descriptor routing must be correct. Camera pipelines depend on many clocks and power domains, so partial enablement can produce capture timeouts.

Test signals: Main and raw camera node binding, capture on RAWA/RAWB paths, runtime PM gate toggling, suspend/resume, and unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-cam.c -->
