# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8450.c

Purpose: This Video CC driver covers SM8450 and SM8475. It registers two Lucid EVO/OLE PLLs, MVS0/MVS1 RCGs, read-only dividers, branch clocks, nested GDSCs, reset controls, and critical CBCRs through the RPM-aware Qualcomm CC path.

Important APIs, types, and functions: Static data includes `clk_alpha_pll` with `.config` pointers, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. `video_cc_sm8450_probe()` switches PLL register layouts and configs for `qcom,sm8475-videocc`, then calls `qcom_cc_probe()`.

Control flow: The generic `qcom_cc_probe()` path handles mapping, PLL/critical clock setup from `driver_data`, and descriptor registration. No manual PM runtime handling appears in this file. Variant handling happens before the common probe by changing PLL `regs` and `config` pointers.

State and persistence: Hardware registers hold PLL, RCG, divider, branch, reset, and GDSC state. The descriptor sets `.use_rpm = true`, so integration includes RPM-managed sequencing. Critical CBCRs keep AHB, XO, and sleep clocks on.

Dependencies and integration: Depends on `qcom,sm8450-videocc.h`, Qualcomm clock core data-driver support, alpha PLL, RCG, divider, branch, reset, GDSC, and platform bus. Video codec firmware depends on the MVS/MVSC power-domain hierarchy.

Risks: SM8475 support mutates static PLL fields. If a future multi-instance platform binds both variants, state could collide. The driver relies on common code honoring `qcom_cc_driver_data` critical CBCR and alpha PLL lists. GDSC parent relationships must match hardware power collapse order.

Test signals: Compile, boot SM8450 and SM8475 targets, verify `use_rpm` probe path configures PLLs, confirm critical clocks stay enabled, check reset delays, and exercise both MVS0 and MVS1 video paths.
