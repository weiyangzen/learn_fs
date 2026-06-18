# sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sdm660.c

## Purpose

This SDM630/SDM660 GPUCC driver registers CXO, two generic alpha GPU PLLs, a special `clk_rcg2_gfx3d` graphics source, RBCPR/RBBM timer clocks, resets, and CX/GX GDSCs.

## Important APIs, types, and functions

Key data includes `gpu_pll0_pll_out_main`, `gpu_pll1_pll_out_main`, `gfx3d_clk_src`, `rbcpr_clk_src`, `rbbmtimer_clk_src`, `gpucc_sdm660_resets`, `gpucc_sdm660_clocks`, `gpu_cx_gdsc`, `gpu_gx_gdsc`, and `gpucc_sdm660_desc`. `gpucc_sdm660_probe()` builds an `alpha_pll_config`, programs PLL0 for 800 MHz and PLL1 for 740 MHz, then calls `qcom_cc_really_probe()`.

## Control flow, state, and persistence

The OF table supports `"qcom,gpucc-sdm660"` and `"qcom,gpucc-sdm630"`. Probe maps registers, programs both PLLs with different L/alpha values, and registers clocks, resets, and GDSCs. State is GPUCC register state and kernel clock/genpd registration until reset or driver removal.

## Dependencies and integration points

Dependencies are Qualcomm alpha PLL, special graphics RCG, branch, reset, GDSC, and SDM660 bindings. GPU GX is a child of CX with clamp, SW/AON reset, CXC, and retention flags. Consumers include graphics, RBCPR voltage control, RBBM timer, and GPU power domains.

## Risks and test signals

Risks are the shared PLL config mutation between PLL0/PLL1, graphics RCG behavior, and GX retention flags. Test both SDM630 and SDM660 DTs, GPU devfreq, RBCPR operation, timer-based GPU idle, reset lines, and power collapse/retention cycles.
