# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sc8280xp.c

## Purpose

This SC8280XP GPUCC driver provides Lucid 5LPE PLL0/PLL1, GMU/hub RCGs, hub dividers, GPU branches, SMMU vote clock, and CX/GX GDSCs, including a GX `vdd-gfx` supply.

## Important APIs, types, and functions

Important objects are `gpu_cc_pll0_config`, `gpu_cc_pll1_config`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_sc8280xp_clocks`, `cx_gdsc`, `gx_gdsc`, and `gpu_cc_sc8280xp_desc`. `gpu_cc_sc8280xp_probe()` uses runtime PM, maps with `qcom_cc_map()`, configures both PLLs, enables CB and CXO branches, and registers via `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The driver matches `"qcom,sc8280xp-gpucc"`. Runtime PM is enabled and resumed before mapping/register access, then released after registration. Probe configures PLLs and always-on clocks, then publishes clocks and GDSCs. State is volatile register state, runtime-PM references, and CCF/genpd registrations.

## Dependencies and integration points

Dependencies include runtime PM, Qualcomm Lucid PLL/RCG/branch/divider/common/GDSC helpers, and SC8280XP bindings. Integration points are GPU/GMU, SMMU, hub clocks, CX/GX power domains, and a regulator-backed GX graphics supply.

## Risks and test signals

Risks are runtime-PM ordering, regulator naming for `vdd-gfx`, always-on branch offsets, and PLL0/PLL1 5LPE programming. Test GPU probe with regulator constraints, suspend/resume, runtime PM, clock summary, and error injection around map/probe to verify PM refs are balanced.
