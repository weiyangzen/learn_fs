# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcm2290.c

## Purpose

This QCM2290 GPUCC driver registers a compact GPU clock tree: Huayra PLL0, GMU and GX graphics RCGs, AHB/CRC/CX/GX/CXO/sleep/SMMU branches, one GX reset, and CX/GX GDSCs.

## Important APIs, types, and functions

Important objects are `gpu_cc_pll0_config`, `gpu_cc_pll0`, `gpu_cc_gmu_clk_src`, `gpu_cc_gx_gfx3d_clk_src`, `gpu_cc_qcm2290_clocks`, `gpu_cc_qcm2290_resets`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpu_cc_qcm2290_desc`. `gpu_cc_qcm2290_probe()` uses `qcom_cc_map()`, runtime PM, `devm_pm_clk_create()`, `pm_clk_add()`, `clk_huayra_2290_pll_configure()`, a GX CXO enable bit, and `qcom_cc_really_probe()`.

## Control flow, state, and persistence

Probe matches `"qcom,qcm2290-gpucc"`, acquires an AHB PM clock, resumes the power domain, configures PLL0, forces `GPU_CC_GX_CXO_CLK`, registers providers, and drops runtime PM. Hardware register state persists only until reset; CCF/genpd objects live for the platform device lifetime.

## Dependencies and integration points

Dependencies include runtime PM/PM clock APIs, Qualcomm clock helpers, `gdsc`, `reset`, and `dt-bindings/clock/qcom,qcm2290-gpucc.h`. Integration is with GPU, GMU, SNOC DVM, SMMU voting, CX/GX power domains, and parent clocks supplied by board DT.

## Risks and test signals

There is an error-path bug: after `qcom_cc_really_probe()` fails, the function still returns `0` after `pm_runtime_put_sync()`. Other risks are missing AHB PM clock, incorrect critical AHB marking, and GX/CX power sequencing. Test failed-probe injection, GPU runtime PM, `pm_clk` acquisition, SMMU access, and clock summary under suspend/resume.
