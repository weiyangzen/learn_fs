# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sdm845.c

Purpose: This is the SDM845 Video CC provider. It registers a Fabia alpha PLL, a Venus source RCG, debug/QDSS/APB/AHB/AXI/core branch clocks, and three GDSC power domains for Venus and two vcodec engines.

Important APIs, types, and functions: Static tables use `clk_alpha_pll`, `clk_rcg2`, `clk_branch`, `gdsc`, and `qcom_cc_desc`. `video_cc_sdm845_probe()` calls `qcom_cc_map()`, `clk_fabia_pll_configure()`, then `qcom_cc_really_probe()`. The exported clock and GDSC indices come from `qcom,videocc-sdm845.h`.

Control flow: The module platform driver binds to `qcom,sdm845-videocc`. During probe the register block is mapped, `video_pll0` at offset `0x42c` is configured with L/alpha values, and CCF resources are registered. Branch operations later enable or disable CBCRs at fixed offsets such as `0x850`, `0x890`, and `0x9b0`.

State and persistence: Persistent state is Video CC register state and GDSC state. `cxcs` arrays associate GDSCs with clock/control registers, allowing the GDSC layer to manage domain collapse around the relevant clock branches. No software state survives driver unload.

Dependencies and integration: It integrates with Linux platform bus, OF matching, Qualcomm CCF helpers, the GDSC framework, and SDM845 video/venus device tree consumers. There is no reset map in this older driver.

Risks: `BRANCH_VOTED` and `BRANCH_HALT` modes are selected per branch and must match hardware. PLL comments leave even/odd outputs disabled in the parent maps, so accidental consumers of those parents would not work. GDSC `POLL_CFG_GDSCR` and `HW_CTRL_TRIGGER` are sensitive to correct register offsets.

Test signals: Compile-test the driver, boot SDM845, confirm `sdm845-videocc` probes after the MMIO resource is available, inspect clk summary for Venus/vcodec clocks, and run video encode/decode workloads while checking for GDSC timeout or halt-check errors.
