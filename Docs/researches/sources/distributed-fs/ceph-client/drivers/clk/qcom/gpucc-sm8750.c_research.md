# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8750.c

## Purpose

This driver registers the Qualcomm SM8750 GPU clock controller. Compared with older GPUCC files it is smaller and exposes a CX GDSC, one Taycan ELU GPU PLL, an even post-divider, GMU and hub RCGs, and the branch clocks required for GPU management, hub, SMMU voting, memory fabric, DEMET, CXO, DPM, and frequency measurement paths.

## Important APIs, types, and functions

The major objects are `gpu_cc_pll0`, `gpu_cc_pll0_out_even`, `gpu_cc_gmu_clk_src`, `gpu_cc_hub_clk_src`, `gpu_cc_hub_div_clk_src`, `gpu_cc_cx_gdsc`, `gpu_cc_sm8750_resets`, `gpu_cc_sm8750_driver_data`, and `gpu_cc_sm8750_desc`. The descriptor sets `.use_rpm = true` and carries `qcom_cc_driver_data` with `alpha_plls` and a list of critical CBCR offsets. `gpu_cc_sm8750_probe()` delegates to the generic `qcom_cc_probe()` path instead of manually mapping and configuring the PLL.

## Control flow, state, and persistence

Probe calls `qcom_cc_probe(pdev, &gpu_cc_sm8750_desc)`. The generic helper uses descriptor metadata to map registers, handle runtime PM, configure the Taycan ELU alpha PLL, enable critical CBCRs, register the CCF clocks, reset controller, and CX GDSC. Hardware register contents hold the active state; the file does not maintain dynamic software state after registration.

## Dependencies and integration points

It depends on the SM8750 GPUCC clock binding, runtime PM, Qualcomm common clock helpers, and parent clocks for `bi_tcxo`, `gpll0_out_main`, and `gpll0_out_main_div`. Consumers are the SM8750 GPU/GMU stack, SMMU vote path, and genpd clients for `GPU_CC_CX_GDSC`.

## Risks and test signals

The critical CBCR list is literal-offset based and must match hardware (`RSCC_XO_AON`, `CXO_AON`, `GX_AHB_FF`, sleep, CB, and RSCC hub clocks). Rate table entries for GMU and hub rely on the even post-divider and fractional GPLL divider support, so parent/selector mistakes can silently produce wrong rates. Test with SM8750 GPU probe, `clk_summary`, runtime PM domain cycling, SMMU traffic, reset assertion/deassertion, and suspend/resume checks that critical branches stay on.
