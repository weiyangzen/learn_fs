# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6350.c

## Purpose

This SM6350/Lagoon GPUCC driver registers Fabia PLL0/PLL1, a CRC fixed factor, GMU/GX graphics RCGs, ACD/CX/GX/VSENSE branches, and CX/GX GDSCs.

## Important APIs, types, and functions

Key objects are `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, `crc_div`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_sm6350_clocks`, `gpu_cc_sm6350_gdscs`, and `gpu_cc_sm6350_desc`. Probe configures both Fabia PLLs, applies GMU wake/sleep CBCR bits at `0x1098`, and registers via `qcom_cc_really_probe()`. Driver init uses `subsys_initcall()` through `gpu_cc_sm6350_init()`.

## Control flow, state, and persistence

The driver matches `"qcom,sm6350-gpucc"`. It registers early at subsystem init, maps GPUCC, programs PLLs, updates GMU CBCR wake/sleep values, and registers clocks and GDSCs. State is volatile GPUCC register state and clock/genpd registration.

## Dependencies and integration points

Dependencies include Qualcomm common, Fabia PLL, RCG, branch, reset header inclusion, GDSC, and SM6350 bindings. Integration includes ACD clocks, GX VSENSE, SMMU/GPU consumers indirectly, and CX/GX domains.

## Risks and test signals

Risks are early init ordering, wake/sleep CBCR constants, critical AHB flag, and GDSC clamp/poll behavior. Test boot ordering, GPU probe, GMU idle/wake, ACD/VSENSE clock visibility, runtime PM, and clock summary after unused-clock disable.
