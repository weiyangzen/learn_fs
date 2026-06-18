<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-cclk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-cclk.c

Purpose: implements CPU CCLK-specific behavior on top of generic Tegra super clocks. It chooses PLLP for low CPU rates, PLLX for high rates, accounts for thermal div2 slowdown, disables unused clock-skipper hardware, and provides pre/post hooks for PLLX rate changes.

Important APIs, types, and functions: exported `tegra_clk_register_super_cclk()`, `tegra_cclk_pre_pllx_rate_change()`, and `tegra_cclk_post_pllx_rate_change()` are the integration surface. Static state is `cclk_super` and `cclk_on_pllx`. CCF ops are `tegra_cclk_super_ops` for Tegra30+ style composite clocks and `tegra_cclk_super_mux_ops` for Tegra20-style mux-only clocks.

Control flow: registration allocates a `tegra_clk_super_mux`, selects ops based on `TEGRA20_SUPER_CLK`, initializes the optional fractional divider at `reg + 4`, clears `SUPER_CDIV_ENB` to disable the clock skipper, registers the clock, and records the singleton pointer. `determine_rate()` compares requested CPU rate with PLLP rate: requests at or below PLLP use PLLP, while higher requests round PLLX and select it. `recalc_rate()` halves the result when the thermal `TSENSOR_SLOWDOWN` bit is active, and bypasses divider math when parent is direct PLLX.

State and persistence: the singleton keeps the registered CPU clock state and whether it was on PLLX during a PLLX rate-change transaction. Hardware state is in CCLK burst/divider registers. Pre-change reparenting temporarily moves CPU to PLLP before PLLX is altered; post-change restores PLLX only if it was previously selected.

Dependencies and integration: relies on `tegra_clk_super_ops`, parent index constants `PLLP_INDEX` and `PLLX_INDEX`, and PLL code calling the pre/post hooks around PLLX rate changes. Tegra20/30 SoC files register CPU super clocks through this API.

Risks and test signals: risks are singleton misuse, missing pre/post PLLX notifications, incorrect parent indexes for a SoC parent array, and rate calculations that hide thermal throttling. Test CPUfreq transitions below and above PLLP, PLLX rate changes while CPU is and is not parented to PLLX, thermal slowdown reporting, and registration rejection on a second CCLK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-cclk.c -->
