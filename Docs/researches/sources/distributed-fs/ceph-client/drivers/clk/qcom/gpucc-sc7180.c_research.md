# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc7180.c

## Purpose

This SC7180 GPUCC driver registers a small GPU clock/power provider: Fabia PLL1, GMU RCG, CXO/CRC/CX GMU/SNOC DVM branches, and CX/GX GDSCs.

## Important APIs, types, and functions

Important items are `gpu_cc_pll1`, `gpu_cc_gmu_clk_src`, `gpu_cc_crc_ahb_clk`, `gpu_cc_cx_gmu_clk`, `gpu_cc_cx_snoc_dvm_clk`, `gpu_cc_cxo_aon_clk`, `gpu_cc_cxo_clk`, `cx_gdsc`, `gx_gdsc`, and `gpu_cc_sc7180_desc`. `gpu_cc_sc7180_probe()` builds the PLL config inline, calls `clk_fabia_pll_configure()`, applies GMU wake/sleep CBCR bits, and registers via `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The compatible is `"qcom,sc7180-gpucc"`. Probe maps GPUCC registers, programs PLL1 to 360 MHz, applies recommended wake/sleep values to the GMU CBCR at `0x1098`, then registers clocks and GDSCs. State is volatile MMIO plus CCF/genpd registrations.

## Dependencies and integration points

The driver depends on Qualcomm Fabia PLL, RCG, branch, common, and GDSC helpers plus SC7180 clock bindings. It integrates with Adreno/GMU and CX/GX power domains; GX power-on is delegated with `gdsc_gx_do_nothing_enable()`.

## Risks and test signals

The inline PLL values and GMU CBCR wake/sleep workaround are the highest-risk hardware constants. Missing resets in this descriptor mean power-domain behavior must be validated carefully. Test GPU probe, GMU idle/wake, suspend/resume, `clk_summary`, and absence of GMU timeout messages.
