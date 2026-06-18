# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-814x.c

Purpose: DM814x/TI81xx clock-control metadata and early ADPLL initialization glue. It defines clkctrl register tables for default, always-on, and Ethernet clock blocks, a small legacy alias table, and initcall sequencing for PLL subsystem population.

Important APIs/types/functions: exports `dm814_clkctrl_data[]`; defines `dm814x_dt_clk_init()`, `dm814x_adpll_early_init()` as `core_initcall`, and `dm814x_adpll_enable_init_clocks()` as `postcore_initcall`. Uses `omap_clkctrl_reg_data`, `ti_dt_clk`, `of_platform_populate()`, and `omap2_clk_enable_init_clocks()`.

Control flow: `dm814x_dt_clk_init()` registers `timer_sys_ck`, disables autoidle, adds aliases, enables no named init clocks, and sets `timer_clocks_initialized`. Later initcalls are gated on that boolean: the core initcall locates the `pllss` node and populates ADPLL platform devices; the postcore initcall obtains and enables `pll040clkout` and `pll290clkout`.

State and persistence: tables are init-only. Persistent state consists of clkctrl registrations, populated ADPLL child devices, and enabled MPU/DDR ADPLL output clocks. `timer_clocks_initialized` is a static sequencing guard.

Dependencies/integration: selected by TI81xx machine support and `dt-bindings/clock/dm814.h`; integrated with `clkctrl.c` through the exported data table. Requires DTS to provide a `pllss` node and clock names matching `pll040clkout` and `pll290clkout`.

Risks: ADPLL population is skipped if the main init did not run, and missing `pllss` or init clocks only logs warnings/errors. The Ethernet clkctrl entry uses offset `0` at a base address, so the base address must be exact.

Test signals: boot DM814x with DT clock debug, confirm `pllss` child devices probe after timers are ready, verify UART/GPIO/I2C/MMC/GPMC clocks can enable, and check warning logs for missing init clocks or clkctrl aliases.
