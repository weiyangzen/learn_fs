# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8350.c

Purpose: This driver describes SM8350 and SC8280XP Video CC hardware. It provides AHB/XO/sleep sources, two Lucid 5LPE PLLs, MVS0/MVS1 clocks and dividers, reset lines, and four retained GDSCs.

Important APIs, types, and functions: The driver uses PM runtime, `qcom_cc_map()`, `clk_lucid_pll_configure()`, `qcom_branch_set_clk_en()`, `qcom_cc_really_probe()`, and OF compatibility checks. Static descriptors include `video_cc_sm8350_clocks`, `video_cc_sm8350_resets`, `video_cc_sm8350_gdscs`, and `video_cc_sm8350_desc`.

Control flow: Probe resumes the device. If compatible is `qcom,sc8280xp-videocc`, it mutates sleep/XO register offsets, PLL VCO tables, and MVS frequency tables before mapping. It then maps registers, configures two PLLs, enables AHB and XO CBCRs, registers clocks/resets/GDSCs, and releases PM runtime.

State and persistence: Register state holds all live behavior. The static driver tables are intentionally mutated for SC8280XP before registration, so probe order matters and the module is not written for independent simultaneous variants in one kernel instance. GDSCs use `RETAIN_FF_ENABLE`, and MVS domains have hardware-triggered power state.

Dependencies and integration: Integrates with DT compatibles `qcom,sm8350-videocc` and `qcom,sc8280xp-videocc`, Qualcomm clock helpers, GDSC, reset framework, PM runtime, and video/CVP consumers.

Risks: Variant mutation of global static objects is the main maintainability risk. Wrong compatible selection changes register offsets and VCO/frequency ceilings. PM runtime references must stay balanced. Read-only dividers depend on hardware defaults.

Test signals: Boot both SM8350 and SC8280XP DTs, confirm variant-specific clocks and CBCR offsets, inspect reset IDs from `qcom,sm8350-videocc.h`, and run video workloads at high MVS rates including suspend/resume.
