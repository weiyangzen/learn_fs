<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra114.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra114.c

Purpose: top-level CAR clock driver for Tegra114. It maps CAR/PMC registers, declares PLL parameter tables, maps Tegra internal clock IDs to DT IDs, registers fixed/root/PLL/peripheral/audio/super clocks, initializes clock defaults, and exposes DFLL DVCO reset plus CPU clock trim controls.

Important APIs, types, and functions: entry point is `tegra114_clock_init()` through `CLK_OF_DECLARE("nvidia,tegra114-car")`. Major helpers are `tegra114_pll_init()`, `tegra114_periph_clk_init()`, `tegra114_clock_apply_init_table()`, CPU CAR ops, DFLL reset assert/deassert, and exported `tegra114_clock_tune_cpu_trimmers_*()` functions. Static data includes PLL params for PLLC/C2/C3/M/P/A/D/D2/U/X/E/RE, `tegra114_clks[]`, `devclks[]`, and `init_table[]`.

Control flow: init maps CAR and PMC, allocates the Tegra clock table for five peripheral banks, initializes oscillator roots and `clk_32k`, registers PLLs and derived outputs, installs Tegra114-specific peripherals such as DSI muxes/gates, EMC mux/MC, MIPI-CAL, and VI sensor, then calls shared peripheral/audio/super-clock init. It registers one special reset for `TEGRA114_RST_DFLL_DVCO`, publishes the OF clock provider, registers legacy clkdev aliases, stores the init-table callback, and installs CPU CAR ops.

State and persistence: global `clk_base`, `pmc_base`, `clks`, `osc_freq`, and `pll_ref_freq` hold runtime clock-controller state. CPU suspend context saves CSITE and CCLKG burst/divider registers and restores them on resume. CPU trimmer functions program finetrim registers and fence through a CAR readback. Hardware PLL state is mostly owned by shared PLL implementations using the static params here.

Dependencies and integration: depends on Tegra DT bindings, `clk.h`, shared fixed/peripheral/audio/super-clock files, PMC node `"nvidia,tegra114-pmc"`, and reset framework hooks from Tegra clock code. DFLL reset is used by the DFLL driver; CPU trimmer symbols are exported for voltage/CPU frequency code.

Risks and test signals: risks are PLL table/reg offset errors, unchecked registration failures, missing PMC mapping, incorrect initial enable bits for DFLL ref/soc needed by I2C5, and CPU trim assumptions noted in comments. Test full boot clock summary, init-table rates, DSI/EMC/MC clocks, DFLL reset control, CPU suspend/resume, and audio/XUSB defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra114.c -->
