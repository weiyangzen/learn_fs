# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-vdo1.c

## Purpose
`clk-mt8188-vdo1.c` provides MT8188 VDO1 clocks for the second display/video-output fabric, including merge, padding, DSC, DP interface, HDMI/eDP/HDCP, and related split paths.

## Important APIs, Types, And Functions
The file defines six VDO1 gate register banks, a large `vdo1_clks` table, `vdo1_desc`, and the platform driver for `mediatek,mt8188-vdosys1`. It uses `mtk_clk_pdev_probe()` and `mtk_clk_pdev_remove()`. `CLK_SET_RATE_PARENT` appears on the DP interface gate.

## Control Flow, State, And Persistence
Probe registers all VDO1 gates through the MediaTek platform-device helper and publishes the provider. State is the onecell clock data and hardware gate bits; remove unregisters the provider and gates.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers are DRM display and external display paths, especially DP/HDMI/eDP/HDCP blocks. Risks are high for multi-output display because gate-bank offsets and parent names must match the hardware data sheet. Test signals include DP/HDMI/eDP modesets, HDCP paths if enabled, unused-clock cleanup, and display suspend/resume.
