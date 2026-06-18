# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk.c

Purpose: shared Rockchip common-clock registration engine. It translates declarative `struct rockchip_clk_branch` and `struct rockchip_pll_clock` tables from SoC files into Linux CCF clocks and providers.

Important APIs/types/functions: `rockchip_clk_register_branch()` builds composite mux/divider/gate clocks. `rockchip_clk_register_frac_branch()` builds fractional divider clocks and optional child muxes. `rockchip_clk_register_factor_branch()` builds fixed-factor plus optional gate clocks. Exported provider APIs include `rockchip_clk_init()`, `rockchip_clk_init_early()`, `rockchip_clk_finalize()`, `rockchip_clk_of_add_provider()`, `rockchip_clk_register_plls()`, `rockchip_clk_register_branches()`, `rockchip_clk_register_late_branches()`, `rockchip_clk_register_armclk()`, `rockchip_clk_register_armclk_multi_pll()`, `rockchip_clk_protect_critical()`, and `rockchip_register_restart_notifier()`.

Control flow: SoC init allocates a provider, then registers PLLs and branches. Branch registration switches on `branch_type`, chooses CRU or auxiliary GRF regmap, creates the relevant CCF object, logs failures, and installs successful clocks in the onecell lookup. Late linked gates become platform devices. Restart uses a reboot notifier that writes the configured reset register.

State and persistence: allocates provider context, onecell clock table, branch helper objects, fractional notifier state, GRF regmap references, and static restart notifier globals. Hardware state persists in CRU/GRF registers.

Dependencies and integration: Linux CCF, syscon regmap, OF clock provider API, restart handlers, platform devices, and Rockchip-specific PLL/CPU/MMC/DDR/inverter/half-divider helpers.

Risks: allocation failures during composite registration can leave partially registered clocks. Fractional child muxes rely on matching parent names; if not found, rate changes may not work. Restart globals support one active Rockchip restart base. Auxiliary GRF selection depends on correct `grf_type`.

Test signals: boot logs without failed clock registrations, correct onecell indexes for DT consumers, rate-change tests on fractional clocks with child muxes, late linked-gate runtime PM behavior, and reboot/reset operation through the registered notifier.
