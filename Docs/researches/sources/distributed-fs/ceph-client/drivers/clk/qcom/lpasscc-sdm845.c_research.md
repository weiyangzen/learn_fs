# sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sdm845.c

## Purpose

This SDM845 LPASSCC driver registers LPASS Q6SS AHB always-on bus clocks and QDSP6SS core/XO/sleep branch clocks. It is an early subsystem clock provider for the SDM845 audio DSP complex.

## Important APIs, types, and functions

Important objects are `lpass_q6ss_ahbm_aon_clk`, `lpass_q6ss_ahbs_aon_clk`, `lpass_qdsp6ss_core_clk`, `lpass_qdsp6ss_xo_clk`, `lpass_qdsp6ss_sleep_clk`, shared `lpass_regmap_config`, `lpass_cc_sdm845_desc`, `lpass_qdsp6ss_sdm845_desc`, and `lpass_cc_sdm845_probe()`. Bus clocks use `BRANCH_VOTED`; QDSP6SS clocks use `BRANCH_HALT_SKIP`.

## Control flow, state, and persistence

Probe registers the LPASS CC descriptor against resource index 0 with regmap name `"cc"`, then registers the QDSP6SS descriptor against resource index 1 with name `"qdsp6ss"`. The driver is registered at `subsys_initcall` time. State is branch enable bits and CCF registrations.

## Dependencies and integration points

Dependencies are SDM845 LPASS clock bindings, indexed DT resources, Qualcomm branch/common helpers, and QDSP6/LPASS audio consumers. It integrates with remoteproc and audio drivers that need Q6SS clocks during boot and reset release.

## Risks and test signals

The main risks are resource index reversal, voted-clock semantics for AHBM/AHBS, and halt-skip behavior hiding real QDSP6 clock issues. Test on SDM845 by checking `clk_summary`, booting ADSP, enabling/disabling Q6SS clocks through runtime paths, and validating suspend/resume and remoteproc restart.
