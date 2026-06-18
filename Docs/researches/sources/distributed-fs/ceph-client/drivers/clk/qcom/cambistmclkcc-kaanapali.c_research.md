# sources/distributed-fs/ceph-client/drivers/clk/qcom/cambistmclkcc-kaanapali.c

## Purpose
`cambistmclkcc-kaanapali.c` registers the Kaanapali camera BIST master-clock controller. It supplies eight camera test/master MCLK sources and branch clocks from a single 960 MHz Rivian EKO-T alpha PLL or the TCXO parent.

## Important APIs, Types, And Functions
Important state includes `cam_bist_mclk_cc_pll0`, `ftbl_cam_bist_mclk_cc_mclk0_clk_src`, eight `clk_rcg2` MCLK source instances, eight `clk_branch` MCLK gates, `cam_bist_mclk_cc_kaanapali_clocks`, critical CBCR list, `cam_bist_mclk_cc_kaanapali_desc`, and `cam_bist_mclk_cc_kaanapali_probe()`. It uses `clk_alpha_pll_rivian_eko_t_ops`, `clk_rcg2_shared_ops`, `clk_branch2_ops`, and `qcom_cc_probe()`.

## Control Flow, State, And Persistence
The descriptor lists PLL data, RCGs, branches, a register map up to `0x5010`, `use_rpm = true`, and a critical sleep-clock CBCR at `0x40e0`. Probe delegates to `qcom_cc_probe()`, which maps MMIO, configures PLLs from driver data, registers clocks, and publishes the provider. Runtime state is MMIO-backed PLL, RCG, and branch configuration. Frequency tables provide 19.2 MHz TCXO, 24 MHz divided PLL, and about 68.57 MHz PLL-main outputs.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include Kaanapali CAMBISTMCLKCC DT bindings, GCC/always-on parent clocks by DT index, qcom common clock code, RPM-aware clock handling, and camera/test clock consumers. Risks include duplicate tables copied across all eight MCLKs, critical CBCR offset errors leaving sleep clock gated, MCLK rate coverage gaps for sensors/tests, and no reset/GDSC coverage despite including headers. Test signals include module probe on `qcom,kaanapali-cambistmclkcc`, all eight MCLKs selectable, 24 MHz sensor-style output validation, sleep clock remaining on, and clk debugfs showing shared RCG behavior.
