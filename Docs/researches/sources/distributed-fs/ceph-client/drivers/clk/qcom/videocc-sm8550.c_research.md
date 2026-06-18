# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8550.c

Purpose: This driver supports SM8550, SM8650, and X1E80100 Video CC. It exports two Lucid OLE PLLs, MVS0/MVS1 RCGs, optional shift/XO clocks, dividers, GDSCs, resets, and critical CBCRs.

Important APIs, types, and functions: It defines variant frequency tables, `clk_alpha_pll` configs, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, four `gdsc`s, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. `video_cc_sm8550_probe()` checks compatibles and mutates PLL L/alpha values, RCG tables, clock-array entries, and critical CBCR tables before invoking `qcom_cc_probe()`.

Control flow: `qcom_cc_probe()` performs common mapping and registration using `.use_rpm = true` and `driver_data`. For X1E80100 only PLL values and MVS tables are changed. For SM8650, shift clocks and `video_cc_xo_clk_src` are added to the exported clock array and the sleep critical CBCR offset changes.

State and persistence: Static tables are modified during probe for variant support. Hardware state includes PLL, RCG, divider, branch, GDSC, and reset registers. Critical clocks are maintained by common Qualcomm CC code rather than manual writes here.

Dependencies and integration: Integrates with `qcom,sm8550-videocc`, `qcom,sm8650-videocc`, and `qcom,x1e80100-videocc` DT compatibles, Qualcomm RPM-aware CC support, reset/GDSC frameworks, and video/CVP consumers.

Risks: Variant-specific mutation is broad: frequency tables, PLL configs, clock exports, and critical CBCRs can diverge. The base clock array intentionally has `VIDEO_CC_XO_CLK_SRC = NULL`, so consumers must not request it except on variants that install it. Reset delays are hardware-sensitive.

Test signals: Boot each compatible, verify exported clock count and NULL slots, check SM8650 shift clocks appear, confirm critical CBCRs, run high-rate video tests, and validate reset/GDSC sequencing under suspend/resume.
