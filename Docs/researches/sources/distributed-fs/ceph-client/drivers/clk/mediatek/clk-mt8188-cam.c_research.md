# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-cam.c

## Purpose
`clk-mt8188-cam.c` provides the MT8188 camera clock-controller drivers for the main CAMSYS block and its RAW/YUV sub-blocks. It maps multiple device-tree compatibles to gate-only clock descriptors used by the camera pipeline.

## Important APIs, Types, And Functions
The file defines `cam_cg_regs`, per-domain `struct mtk_gate` arrays for main, raw A/B, and yuv A/B clocks, and `struct mtk_clk_desc` instances. `cam_sys_rst_desc` exposes CAM reset lines from `mt8188-resets.h`. The platform driver binds `mediatek,mt8188-camsys`, `camsys-rawa`, `camsys-rawb`, `camsys-yuva`, and `camsys-yuvb` through `mtk_clk_simple_probe()`/`mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe is data-driven: OF match selects one descriptor, the common MediaTek helper maps registers, allocates onecell clock storage, registers gates, optional reset support for the main descriptor, and publishes clocks to OF consumers. Persistent kernel state is the registered clock hardware, gate register offsets, and reset-controller metadata until driver remove unregisters it.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-gate`, `clk-mtk`, `clk-mt8188` IDs, CAM reset bindings, and camera DT nodes. Risks are incorrect parent names such as top camera clocks, wrong gate bit positions, or reset maps that break camera sensor/ISP bring-up. Test signals include DT binding probe for all five compatibles, `clk_summary` CAM gate visibility, reset-controller use by camera drivers, and camera stream start/stop power gating.
