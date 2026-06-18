<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-super.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-super.c

Purpose: provides generic Tegra "super clock" muxes used for CPU and system clock burst-policy registers. A super clock has state-specific parent selector fields for idle/run/IRQ/FIQ states and, in the full composite form, a fractional divider in the adjacent register.

Important APIs, types, and functions: exported `tegra_clk_super_ops`, `tegra_clk_register_super_mux()`, and `tegra_clk_register_super_clk()` are the integration surface. The main data carrier is `struct tegra_clk_super_mux` with register address, selector width, lock, PLLX/div2 indexes, embedded `tegra_clk_frac_div`, and optional flags such as `TEGRA_DIVIDER_2` and `TEGRA210_CPU_CLK`. Key callbacks are `clk_super_get_parent()`, `clk_super_set_parent()`, `clk_super_restore_context()`, and the composite divider wrappers.

Control flow: parent get/set reads the burst-policy register, requires hardware state to be RUN or IDLE, chooses the field offset for that state, and masks by configured selector width. For low-power CPU clocks with `TEGRA_DIVIDER_2`, PLLX and PLLX/2 are represented as separate logical parents even though hardware uses a bypass bit plus PLLX selector. `set_parent()` refuses direct PLLX-to-PLLX/2 changes, toggles `SUPER_LP_DIV2_BYPASS` only from another parent, and delays for hardware settling. Tegra210 CPU clocks enable PLLP CPU branches before selecting PLLP out0/out4 and disable those branches after moving away.

State and persistence: persistent state is in the CAR burst-policy register and optional divider register at `reg + 4`. The restore path replays divider state first for full super clocks and then restores the selected parent. Registration allocates a permanent `tegra_clk_super_mux` and uses `clk_register()` or `tegra_clk_dev_register()`.

Dependencies and integration: uses CCF mux/divider callbacks, Tegra fractional divider ops, Tegra CPU PLLP branch control, and `clk.h` flag definitions. Gen4/gen5 SoC code registers `sclk`, `cclk_g`, and `cclk_lp` through these APIs; CPU-specific wrappers in `clk-tegra-super-cclk.c` reuse `tegra_clk_super_ops`.

Risks and test signals: important risks are `BUG_ON()` if used while hardware reports IRQ/FIQ state, unsafe LP PLLX/div2 transitions, stale PLLP CPU branch gates, and wrong selector width or parent ordering. Test parent transitions in RUN and IDLE, LP PLLX/div2 negative paths, suspend/resume restore, and Tegra210 CPU parent moves to and from PLLP outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-super.c -->
