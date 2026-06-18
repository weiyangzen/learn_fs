# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8250.c

Purpose: This SM8250 Video CC driver registers two Lucid PLLs, MVS0/MVS1 sources and read-only dividers, core clocks, four GDSCs, and reset controls for CVP/MVS blocks.

Important APIs, types, and functions: It uses `clk_alpha_pll`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, and `qcom_cc_desc`. `video_cc_sm8250_probe()` enables PM runtime, maps registers, configures both PLLs with `clk_lucid_pll_configure()`, keeps AHB and XO clocks on via `qcom_branch_set_clk_en()`, registers the CC descriptor, and drops the PM runtime reference.

Control flow: The probe path runs only for `qcom,sm8250-videocc`. After PLL setup, clock consumers use RCG tables for MVS0 and MVS1 and fixed hardware dividers for MVS/MVSC branches. Reset users trigger BCR or ARES entries through the Qualcomm reset framework.

State and persistence: PLL config, branch state, read-only divider values, reset bits, and GDSC power state are all in hardware registers. The driver does not maintain runtime caches except static object tables.

Dependencies and integration: It depends on PM runtime, regmap, Qualcomm alpha PLL/RCG/divider/branch/GDSC/reset helpers, and DT clock/reset IDs from `qcom,videocc-sm8250.h`.

Risks: `clk_regmap_div_ro_ops` means divider values must be programmed by firmware or hardware reset defaults; the driver cannot correct bad divider state. Hard-coded keepalive CBCR offsets must remain valid. GDSC hierarchy is flat here, unlike later drivers with parented MVS domains.

Test signals: Compile-test, boot SM8250, check AHB/XO clocks remain enabled, request supported MVS rates, verify reset controls with video firmware bring-up, and watch for PM runtime imbalance or GDSC failures.
