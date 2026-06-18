# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8150.c

Purpose: This SM8150 Video CC driver provides the Trion PLL, Iris source, MVS/MVSC core clocks, reset lines, and three GDSC domains for the video subsystem.

Important APIs, types, and functions: The file uses `devm_pm_runtime_enable()`, `pm_runtime_resume_and_get()`, `qcom_cc_map()`, `clk_trion_pll_configure()`, `regmap_update_bits()`, and `qcom_cc_really_probe()`. It defines `qcom_reset_map` entries for MVSC interface/MVS reset lines and `gdsc` entries for Venus, vcodec0, and vcodec1.

Control flow: Probe enables runtime PM and resumes the device before touching registers. It maps the block, configures the PLL, forces `VIDEO_CC_XO_CLK` on at `0x984`, registers the CC descriptor, then runtime-suspends the device with `pm_runtime_put_sync()`.

State and persistence: Video CC register state is modified during probe and by future CCF operations. Runtime PM controls access around probe. The reset map exposes block-reset bits and an MVSC core clock async reset with delay. No persistent software configuration is stored.

Dependencies and integration: The driver needs platform PM runtime, regmap, Qualcomm reset/GDSC/common helpers, and `qcom,videocc-sm8150.h`. Video devices depend on these clocks and GDSCs to power their codec paths.

Risks: Probe error paths must balance PM runtime references; the driver handles map failure and post-register cleanup with `pm_runtime_put_sync()`. The XO keepalive is a raw register update. Branch set selections are minimal compared to newer MVS drivers, so missing AHB/AXI clocks must be accounted for by hardware design or other providers.

Test signals: Build and boot SM8150, verify PM runtime does not leave the device active after probe, confirm reset controls exist, inspect the always-on XO CBCR, and test video across suspend/resume.
