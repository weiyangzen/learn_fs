# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo1.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-vdo1.c

### Purpose
`clk-mt8195-vdo1.c` describes the second MT8195 video-output clock domain. It gates VDO1 SMI/LARB, MDP RDMA, merge, HDR front/back-end, DPI, DP, monitor, HDMI-DPI, slow 26 MHz, and cross-domain async clocks.

### Important APIs, Types, And Functions
The core objects are five `mtk_gate_regs` banks, `GATE_VDO1_*` macros, `vdo1_clks`, and `vdo1_desc`. Most gates use `mtk_clk_gate_ops_setclr`; the HDMI DPI gate uses `mtk_clk_gate_ops_no_setclr_inv` against the 0x400 register; the DP interface gate carries `CLK_SET_RATE_PARENT`. The platform driver uses `mtk_clk_pdev_probe()` with a platform ID table.

### Control Flow, State, And Persistence
The driver is passive after module registration. Common probe reads `driver_data`, registers the fixed gate table, and makes a onecell provider. Clock enable state is stored only in the SoC gate registers; no software cache or nonvolatile state is maintained.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on MT8195 clock IDs, parent names `top_vpp`, `top_dp`, `clk26m`, and `hdmi_txpll`, and display/HDMI/DP consumers. Risks include the inverted no-setclr HDMI gate being modeled incorrectly, rate-parent behavior for DP, and fragile long clock names used by consumers. Test signals include HDMI/DPI and DP output bring-up, VDO1 SMI clock availability, debugfs clock parent/rate checks, and module remove/unbind cleanup.
