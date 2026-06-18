<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-cam.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-cam.c

Purpose: This file exposes MT8183 camera subsystem gates.

Important APIs, types, and functions: `cam_cg_regs` defines the camera gate register bank; `GATE_CAM` builds `cam_clks`; `cam_desc` is attached to `mediatek,mt8183-camsys`; probe/remove use MediaTek simple helpers.

Control flow: The OF platform driver registers camera gates and publishes them to camera sensor, ISP, SENINF, and memory-interface consumers.

State and persistence behavior: Gate state is volatile MMIO state. Provider state is runtime-only and removed on unbind.

Dependencies and integration points: It depends on MT8183 clock IDs, common gate helpers, topckgen camera parents, camera pipelines, power domains, and larb/IOMMU paths.

Risks and edge cases: Camera pipelines often need multiple gates and memory clocks; missing one gate can produce timeouts rather than obvious probe failure. Parent/gate bit accuracy is critical.

Test signals: Camera capture, SENINF/ISP probing, runtime PM gate transitions, suspend/resume, and clock provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-cam.c -->
