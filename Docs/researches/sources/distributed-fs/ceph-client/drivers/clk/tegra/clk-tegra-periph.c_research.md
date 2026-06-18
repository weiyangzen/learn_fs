<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-periph.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-periph.c

Purpose: centralizes Tegra peripheral clock registration data shared across multiple SoCs. It defines mux parent tables, per-peripheral composite init rows, simple gate rows, PLLP and PLLP-out branches, and the exported `tegra_periph_clk_init()` that SoC files call after root PLLs exist.

Important APIs, types, and functions: the public API is `tegra_periph_clk_init()`. Internal helpers are `init_pllp()`, `periph_clk_init()`, `gate_clk_init()`, and `div_clk_init()`. Tables include `periph_clks[]`, `gate_clks[]`, `div_clks[]`, and `pllp_out_clks[]`. Macros such as `MUX`, `MUX8`, `INT`, `UART`, `I2C`, `XUSB`, `AUDIO`, `NODIV`, `GATE`, and `DIV8` produce `struct tegra_periph_init_data` using `TEGRA_INIT_DATA_TABLE()`.

Control flow: `tegra_periph_clk_init()` registers PLLP and PLLP outputs first, then iterates data tables. For each composite peripheral clock it checks the DT clock ID, finds the proper enable/reset bank with `get_reg_bank()`, installs the bank into the embedded gate, and calls `tegra_clk_register_periph_data()`. Gate-only and divider-only rows use specialized Tegra gate and divider constructors. `init_pllp()` registers `pll_p`, divider plus `pll_out` pairs, Tegra210's `pll_p_out_cpu`-based CPU branch topology, and HSIO/XUSB gates.

State and persistence: most state is encoded in static init data and hardware CAR source, enable, and reset registers. Gate refcounts use the global `periph_clk_enb_refcnt`. Spinlocks protect shared PLLP_OUT registers. The function writes no long-lived software state beyond registered CCF clock objects.

Dependencies and integration: called by Tegra20/30/114/124/210 SoC init paths with a SoC clock presence table and PLLP params. It integrates with `clk-periph.c`, `clk-periph-gate.c`, `clk-divider`, `clk-pll`, `clk-id.h`, and DT clock IDs. The mux tables encode SoC-specific parent selector holes, so table order and `_idx` maps are part of the ABI.

Risks and test signals: risks include duplicate or wrong clock IDs, wrong parent selector maps, gate flags such as `TEGRA_PERIPH_ON_APB` or `TEGRA_PERIPH_NO_RESET` on the wrong device, and the apparent `iqc2` row using `tegra_clk_iqc1`. Test by validating all present DT IDs resolve, checking parent/rate/gate operations for representative UART/I2C/SDMMC/XUSB/audio/display clocks, inspecting reset behavior, and booting SoCs that select different variants of the same clock name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-periph.c -->
