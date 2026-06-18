# sources/distributed-fs/ceph-client/drivers/clk/qcom/ipq-cmn-pll.c

## Purpose

This driver controls the IPQ CMN PLL block used by networking hardware. The CMN PLL receives a reference clock from the board or Wi-Fi block, programs the PLL for a 12 GHz internal rate, and exposes fixed-rate outputs for XO, sleep, Ethernet PHY/switch, PCS, NSS, PPE, and GCC consumers on IPQ5018/IPQ5424/IPQ6018/IPQ8074/IPQ9574.

## Important APIs, types, and functions

Key types are `cmn_pll_fixed_output_clk` and `clk_cmn_pll`. Important functions are `ipq_cmn_pll_find_freq_index()`, `clk_cmn_pll_recalc_rate()`, `clk_cmn_pll_determine_rate()`, `clk_cmn_pll_set_rate()`, `ipq_cmn_pll_clk_hw_register()`, `ipq_cmn_pll_register_clks()`, `ipq_cmn_pll_clk_probe()`, and `ipq_cmn_pll_clk_remove()`. The clock ops validate supported parent reference rates, program reference index/divider fields, enable lock detection, reset the analog block, and poll `CMN_PLL_CLKS_LOCKED`.

## Control flow, state, and persistence

Probe enables runtime PM, creates PM clock management, adds `"ahb"` and `"sys"` clocks, resumes the block, registers the programmable `cmn_pll` and fixed-rate output clocks, adds an OF onecell provider, then drops the runtime PM reference. Remove unregisters non-devm fixed-rate outputs. Persistent state is the PLL reference selection, divider/reset/lock registers, and fixed-output CCF registrations.

## Dependencies and integration points

Dependencies include regmap, runtime PM, PM clocks, assigned clock rates from DT, and IPQ CMN PLL binding IDs. It integrates with GCC, PPE/NSS, Ethernet PHY/switch, PCS, XO, and sleep-clock consumers.

## Risks and test signals

Unsupported or misdescribed reference clock rates cause `determine_rate()` or `set_rate()` failures. The 96 MHz path has special divider programming, and lock polling failure indicates bad board reference or register access. Test by assigning the CMN PLL to 12 GHz in DT, validating every fixed output rate in `clk_summary`, checking runtime PM AHB/SYS clock handling, exercising Ethernet/NSS/PPE traffic, and verifying remove/unbind does not leak fixed-rate clocks.
