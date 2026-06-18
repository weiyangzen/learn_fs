<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124.c

Purpose: top-level CAR clock driver for Tegra124 and Tegra132. It shares most registration for both SoCs, declares PLL/root/peripheral data, registers Tegra124-specific EMC clocking, exposes DFLL DVCO reset, and handles Tegra132 differences where CPU clocks live outside CAR.

Important APIs, types, and functions: `tegra124_clock_init()` and `tegra132_clock_init()` are declared with `CLK_OF_DECLARE`. Shared phases are `tegra124_132_clock_init_pre()` and `_post()`. Major helpers are `tegra124_pll_init()`, `tegra124_periph_clk_init()`, `tegra124_clock_apply_init_table()`, `tegra132_clock_apply_init_table()`, `tegra124_clk_src_onecell_get()`, CPU CAR ops, and DFLL reset assert/deassert. Static data includes PLL params for PLLX/C/C2/C3/C4/M/E/RE/P/A/D/D2/DP/U, `tegra124_clks[]`, `devclks[]`, SOR parent data, and init tables.

Control flow: pre-init maps CAR/PMC, allocates a six-bank clock table, initializes oscillator and fixed roots, registers all PLLs and derived outputs, registers custom peripherals such as xusb_ss_div2, DPAUX, DSI gates, MC, CML0/1, SOR0, and shared peripherals/audio. It forces PLLD as the DSI source for Tegra124/132. Post-init registers gen4 super clocks, special DFLL reset, a custom OF provider, the EMC clock, clkdev aliases, and CPU CAR ops. Tegra124 sets the full init table; Tegra132 marks CAR CPU/PLLX clocks absent before post-init and uses a smaller init table.

State and persistence: global mapped bases and `clks` hold runtime controller state. CPU suspend context saves/restores CSITE and CCLKG burst/divider registers. The custom onecell provider returns `-EPROBE_DEFER` for EMC until the EMC timing callbacks are present. Hardware PLL and peripheral state is programmed through shared clock implementations.

Dependencies and integration: depends on Tegra124 DT clock/reset bindings, PMC node, shared fixed/peripheral/audio/super-clock files, `tegra124_clk_register_emc()`, and reset framework glue. Consumer-visible DT IDs are selected by `tegra124_clks[]`; legacy clkdev aliases support non-DT users and debug tooling.

Risks and test signals: risks include unchecked registration errors, Tegra132 mutation of the shared `tegra124_clks[]` table after pre-init, PLLSS parameter mistakes for display/storage PLLs, EMC provider ordering, and init-table differences between Tegra124 and Tegra132. Test both compatibles, EMC probe deferral, reset ID behavior, CPU suspend/resume, SOR/DSI/display clocks, XUSB/SATA defaults, and complete clock summary against DT IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124.c -->
