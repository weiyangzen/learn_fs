# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8750.c

Purpose: This is the SM8750 Video CC driver. It exposes a Taycan ELU PLL, AHB/XO/sleep sources, MVS0/MVS0C clocks including freerun and shift branches, two GDSCs, reset controls, and critical CBCRs.

Important APIs, types, and functions: It uses `clk_alpha_pll_taycan_elu_ops`, `clk_rcg2`, `clk_regmap_div_ro_ops`, regular `clk_branch`, `clk_mem_branch` with `clk_branch2_mem_ops`, `gdsc`, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. `clk_sm8750_regs_configure()` programs shifter-done fields and an extra register bit through `regmap_update_bits()`. `video_cc_sm8750_probe()` calls `qcom_cc_probe()`.

Control flow: The driver is registered at `subsys_initcall`, earlier than normal module platform registration. Common Qualcomm CC code maps and registers resources, configures the alpha PLL and critical clocks from `driver_data`, and invokes the custom register configuration callback.

State and persistence: Hardware register state includes PLL programming, RCG/divider state, branch memory enable/ack bits, GDSC state, reset bits, and callback-programmed delay accumulator fields. The module has no dynamic state beyond static descriptors.

Dependencies and integration: Requires `qcom,sm8750-videocc.h`, Qualcomm alpha PLL/RCG/divider/mux/branch memory helpers, GDSC, reset, platform bus, and RPM-aware common CC support.

Risks: This newer driver uses memory branch semantics for `video_cc_mvs0_freerun_clk`; ack polarity and masks must match hardware. Custom register writes are unguarded by variant checks. `subsys_initcall` changes probe timing relative to dependencies. Reset entries use compact initializer forms, increasing the need to verify bit positions.

Test signals: Boot SM8750, verify early platform driver registration, inspect critical AHB/XO/sleep clocks, request MVS0/MVS0C clocks and freerun paths, and validate register callback effects through vendor debug or hardware behavior.
