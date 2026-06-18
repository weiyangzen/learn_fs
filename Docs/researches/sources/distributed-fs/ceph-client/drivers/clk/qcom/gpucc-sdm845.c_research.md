# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sdm845.c

## Purpose

This SDM845 GPUCC driver is a small provider for Fabia PLL1, GMU RCG, CXO/CX GMU/GX power-domain related clocks, and CX/GX GDSCs.

## Important APIs, types, and functions

The relevant objects are `gpu_cc_pll1_config`, `gpu_cc_pll1`, `gpu_cc_gmu_clk_src`, `gpu_cc_cxo_clk`, `gpu_cc_cx_gmu_clk`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, `gpu_cc_sdm845_clocks`, and `gpu_cc_sdm845_desc`. Probe maps registers, calls `clk_fabia_pll_configure()`, updates GMU CBCR wake/sleep bits at `0x1098`, and registers with `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The driver matches `"qcom,sdm845-gpucc"`. Probe configures the PLL and recommended GMU wake/sleep settings before publishing clocks and GDSCs. Runtime state is entirely MMIO plus CCF/genpd registrations.

## Dependencies and integration points

Dependencies include Qualcomm common, Fabia PLL, branch, RCG, GDSC helpers, and SDM845 clock bindings. GX uses clamp, AON reset, and POLL_CFG_GDSCR flags, with power-on delegated to `gdsc_gx_do_nothing_enable()`.

## Risks and test signals

The driver relies on exact PLL and CBCR workaround constants; mistakes can cause GMU boot or idle failures. Risks also include GDSC clamp/reset sequencing. Test Adreno probe, GMU firmware load, runtime PM, suspend/resume, clock summary, and no GMU timeout or stuck GDSC messages.
