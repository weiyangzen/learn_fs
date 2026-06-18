# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc7280.c

## Purpose

This SC7280 LPASSCC driver registers top LPASS and QDSP6SS branch clocks. It covers the LPI Q6 AXIM high-speed top clock and QDSP6 core, XO, and sleep clocks, with optional QDSP6SS registration depending on ADSP PIL mode.

## Important APIs, types, and functions

Key objects are `lpass_top_cc_lpi_q6_axim_hs_clk`, `lpass_qdsp6ss_core_clk`, `lpass_qdsp6ss_xo_clk`, `lpass_qdsp6ss_sleep_clk`, shared `lpass_regmap_config`, `lpass_cc_top_sc7280_desc`, `lpass_qdsp6ss_sc7280_desc`, and `lpass_cc_sc7280_probe()`. The QDSP6SS branches use `BRANCH_HALT_SKIP` because halt status does not toggle until LPASS leaves reset.

## Control flow, state, and persistence

Probe enables runtime PM, creates PM clock support, adds the `"iface"` PM clock, resumes the device, optionally registers QDSP6SS clocks from resource index 0 when `qcom,adsp-pil-mode` is absent, registers top CC from resource index 1, then drops the runtime PM reference. On failure it releases runtime PM and destroys PM clock state.

## Dependencies and integration points

The driver depends on SC7280 LPASS binding IDs, indexed MMIO resources, runtime PM, the iface clock, and Qualcomm common clock helpers. It integrates with ADSP/QDSP6 remoteproc, LPASS top bus users, and audio subsystem power sequencing.

## Risks and test signals

Risks are incorrect resource index ordering, missing iface clock, and wrong ADSP PIL mode behavior causing duplicate or missing QDSP6 clock providers. Test both PIL and non-PIL DT modes, inspect `clk_summary`, boot ADSP remoteproc, verify QDSP6 core/XO/sleep enables while LPASS is in reset and out of reset, and run suspend/resume.
