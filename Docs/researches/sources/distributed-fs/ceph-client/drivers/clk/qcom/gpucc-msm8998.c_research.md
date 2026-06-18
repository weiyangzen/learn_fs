# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-msm8998.c

## Purpose

This MSM8998 GPUCC driver provides GPU PLL0, graphics/RBCPR/RBBM timer/isense RCGs and branches, CX/GX GDSCs, and GPU reset lines. It is the clock and power-domain provider for the MSM8998 Adreno block.

## Important APIs, types, and functions

Key objects include `gpucc_cxo_clk`, `gpupll0`, `gpupll0_out_even`, `rbcpr_clk_src`, `gfx3d_clk_src`, `rbbmtimer_clk_src`, `gfx3d_isense_clk_src`, branch clocks, `gpu_cx_gdsc`, `gpu_gx_gdsc`, `gpucc_msm8998_resets`, and `gpucc_msm8998_desc`. `gpucc_msm8998_probe()` manually maps with `qcom_cc_map()`, writes two GPU wrapper bits, then calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The platform driver matches `"qcom,msm8998-gpucc"`. Probe maps registers, forces peripheral logic on to avoid performance-counter corruption, tweaks the droop detector/leakage bit, and registers clocks, resets, and GDSCs. State is MMIO clock/reset/power-domain state until reset; no software persistence is implemented.

## Dependencies and integration points

It uses Qualcomm regmap clock primitives, Fabia PLL ops, resets, GDSC, and `dt-bindings/clock/qcom,gpucc-msm8998.h`. GPU CX is votable and GX is a child domain with clamp, SW/AON reset, CXC, and retention-related behavior. Consumers include GPU core, devfreq/RBCPR, isense, RBBM timer, and GPU SMMU paths.

## Risks and test signals

The two probe-time writes are fragile hardware workarounds; wrong offsets can corrupt clock control. Other risks are Fabia PLL programming, GDSC reset sequencing, and retention flags. Test GPU bring-up, perf counters, devfreq voltage scaling, power collapse/retention, and `clk_summary` rates for `gfx3d_clk` and RBCPR.
