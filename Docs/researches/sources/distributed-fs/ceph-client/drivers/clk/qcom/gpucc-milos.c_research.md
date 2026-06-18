# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-milos.c

## Purpose

This driver is the GPU clock controller for Milos. It exposes GPU PLL0, FF/GMU/hub RCGs, read-only hub dividers, CX/GX/ACD/RCG branch clocks, SMMU vote clock, resets, and a single CX GDSC to the common clock and genpd frameworks.

## Important APIs, types, and functions

The main data is `gpu_cc_pll0_config`, `gpu_cc_pll0`, `gpu_cc_pll0_out_even`, parent maps, `ftbl_gpu_cc_*`, `gpu_cc_milos_clocks`, `gpu_cc_milos_resets`, `gpu_cc_milos_gdscs`, `gpu_cc_milos_critical_cbcrs`, `gpu_cc_milos_driver_data`, and `gpu_cc_milos_desc`. Probe is a thin `gpu_cc_milos_probe()` wrapper around `qcom_cc_probe()`, which uses the descriptor and driver-data PLL/critical-CBCR lists.

## Control flow, state, and persistence

Module load binds `"qcom,milos-gpucc"`, maps the register space through the Qualcomm CC helper, configures/registers clocks and resets, and publishes the GDSC. Runtime state is hardware register state plus CCF/genpd registrations; nothing is persisted beyond reset. The descriptor sets `.use_rpm = true`, so RPM/PM coordination is part of registration.

## Dependencies and integration points

The file depends on Qualcomm clock helpers (`clk-alpha-pll`, `clk-rcg`, `clk-branch`, regmap divider/mux, `common`, `gdsc`, `reset`) and `dt-bindings/clock/qcom,milos-gpucc.h`. Consumers are the Adreno GPU, GMU, GPU SMMU, MEMNOC graphics path, and GPU power-domain code.

## Risks and test signals

Risks are PLL type/config mismatches, wrong critical CBCR addresses, missing RPM voting, or GDSC wait/retain flag mistakes causing GPU resume hangs. Test by booting Milos DT, confirming GPU probe, checking `clk_summary` for GMU/hub/FF paths, exercising GPU runtime suspend/resume, and validating reset/GDSC toggles do not wedge CX.
