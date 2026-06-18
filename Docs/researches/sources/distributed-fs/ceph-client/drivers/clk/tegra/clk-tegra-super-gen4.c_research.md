<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-gen4.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-gen4.c

Purpose: registers generation 4 and 5 Tegra super-clock trees: system clock (`sclk`), AHB/APB dividers and gates (`hclk`, `pclk`), CPU cluster super muxes (`cclk_g`, `cclk_lp`), PLLX, and `pll_x_out0`.

Important APIs, types, and functions: exported `tegra_super_clk_gen4_init()` and `tegra_super_clk_gen5_init()` call `tegra_super_clk_init()` with `tegra_super_gen_info` describing parent arrays and counts. Internal helpers are `tegra_sclk_init()` and `tegra_super_clk_init()`. Parent arrays differ between gen4 and gen5, especially use of PLLC4 and DFLL CPU output.

Control flow: `tegra_super_clk_init()` optionally registers `cclk_g` and `cclk_lp` with `tegra_clk_register_super_mux()`, using Tegra210-specific CPU branch handling for gen5 `cclk_g` and LP div2 semantics for gen4 `cclk_lp`. It then registers SCLK: either as `sclk_mux` plus divider `sclk`, or as a mux-only critical `sclk` when no separate mux ID exists. HCLK and PCLK are dividers plus gates in `SYSTEM_CLK_RATE`, protected by `sysrate_lock`. When enabled by build config, it registers PLLX and fixed-factor `pll_x_out0`.

State and persistence: state lives in CAR burst-policy, system-rate, and PLLX registers. `sclk`, `hclk`, and `pclk` are marked critical where required to avoid disabling system buses. There is no local suspend storage; registered super-clock/divider ops handle restore where supported.

Dependencies and integration: used by Tegra20/30/114/124/210 SoC init after oscillator and PLLP infrastructure are present. It relies on clock table presence checks to decide which variants to register and on `CONFIG_ARCH_TEGRA_*` to compile PLLX registration paths.

Risks and test signals: risks include parent array/index mismatches, missing critical flags on bus clocks, gen5 CPU PLLP branch handling only being attached to `cclk_g`, and build-config-specific PLLX registration differences. Test `sclk`/`hclk`/`pclk` rates, CPU parent switches, debug clock summaries for gen4 and gen5 SoCs, and suspend/resume of bus clock hierarchy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-gen4.c -->
