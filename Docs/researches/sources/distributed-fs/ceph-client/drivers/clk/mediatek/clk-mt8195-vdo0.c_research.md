# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo0.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo0.c

### Purpose
`clk-mt8195-vdo0.c` provides the MT8195 VDO0 video-output clock controller. It exposes gates for display overlay, color, correction, AAL, gamma, dither, WDMA/RDMA, DSI, DSC, merge, DP interface, SMI, monitor, and async-link blocks.

### Important APIs, Types, And Functions
The file is table driven around `struct mtk_gate_regs`, `GATE_VDO0_*` macros, `vdo0_clks`, and `vdo0_desc`. It uses `mtk_clk_gate_ops_setclr`, plus `GATE_MTK_FLAGS` for the DP interface clock with `CLK_SET_RATE_PARENT`. Registration is through a platform ID table whose `driver_data` points at `vdo0_desc`, and the driver uses `mtk_clk_pdev_probe()` and `mtk_clk_pdev_remove()`.

### Control Flow, State, And Persistence
Probe is delegated to the common MediaTek platform-clock helper, which maps the platform resource, allocates onecell clock data, registers every gate in `vdo0_clks`, and publishes the provider to consumers. Runtime state is the hardware gate bits in three set/clear/status banks at 0x100, 0x110, and 0x120 ranges; the driver has no persistent storage beyond registered clock objects.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are `dt-bindings/clock/mt8195-clk.h`, the common MediaTek gate framework, and parent clocks such as `top_vpp`, `top_dsi_occ`, and `top_edp`. Risks are wrong bit shifts, missing parent names, and DP rate propagation failures. Test signals include boot-time provider registration, display pipeline probe success, clk summary showing VDO0 gates, DP/DSI enable sequences, and suspend/resume gate status.
