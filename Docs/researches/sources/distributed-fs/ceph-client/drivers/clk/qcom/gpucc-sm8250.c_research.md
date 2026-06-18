# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8250.c

## Purpose

This SM8250 GPUCC driver registers Lucid PLL1, GMU RCG, AHB/CRC/CX APB/GMU/SNOC/CXO/GX GMU/SMMU branches, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Key objects are `gpu_cc_pll1_config`, `gpu_cc_pll1`, `gpu_cc_gmu_clk_src`, branch clocks, `gpu_cc_sm8250_resets`, `gpu_cc_sm8250_gdscs`, and `gpu_cc_sm8250_desc`. Probe maps GPUCC, configures PLL1 with `clk_lucid_pll_configure()`, applies GMU wake/sleep CBCR bits, and calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The compatible is `"qcom,sm8250-gpucc"`. Probe programs PLL1, sets recommended wake/sleep values at `0x1098`, and registers clocks, resets, and GDSCs. State is volatile register contents and kernel CCF/genpd/reset registrations.

## Dependencies and integration points

Dependencies are Qualcomm common, Lucid PLL, branch, RCG, reset, GDSC, and SM8250 bindings. It integrates with GPU/GMU, SMMU vote clock, CX/GX domains, and reset consumers for CX/GX/ACD-style controls.

## Risks and test signals

Risks are PLL1 configuration, GMU CBCR workaround, voted halt checks, and GX clamp/AON/poll GDSC flags. Test GPU firmware boot, devfreq, SMMU mappings, suspend/resume, reset controls, and clock summary for GMU and SMMU vote clocks.
