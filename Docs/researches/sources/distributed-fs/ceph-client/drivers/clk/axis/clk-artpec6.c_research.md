<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axis/clk-artpec6.c -->
# sources/distributed-fs/ceph-client/drivers/clk/axis/clk-artpec6.c

Purpose: This file implements ARTPEC-6 clock initialization. It performs an early fixed-clock setup needed before all platform devices probe, then completes the clock table in a built-in platform driver.

Important APIs, types, and functions: `artpec6_clkctrl_drvdata` stores the clock table, syscon base, onecell provider data, and I2S mux lock. `of_artpec6_clkctrl_setup()` is registered with `CLK_OF_DECLARE_DRIVER()` and initializes CPU, CPU peripheral, UART, SPI, debug, and onecell provider state. `artpec6_clkctrl_probe()` completes clocks for NAND, Ethernet, DMA, PTP, SD, I2S, I2C, timer, and fractional-divider input. It uses `clk_register_fixed_factor()`, `clk_register_fixed_rate()`, `clk_register_mux()`, and `of_clk_add_provider()`.

Control flow: Early setup requires the `sys_refclk` parent, allocates a global `clkdata`, initializes every table slot to `ERR_PTR(-EPROBE_DEFER)`, maps the syscon, reads strap-selected PLL mode from the syscon register, derives CPU PLL factors, registers early clocks, and publishes the onecell provider. Later probe reuses the global `clkdata`, resolves optional I2S parents, initializes the I2S mux lock, registers remaining fixed and mux clocks, optionally programs the I2S mux register at offset `0x14`, and reports non-defer registration failures.

State and persistence behavior: The global `clkdata` persists across early declaration and platform probe. Hardware strap state determines CPU rate factors and is read only once. I2S mux selection may be locked to internal or external parent by writing syscon bits when only one parent is present.

Dependencies and integration points: It depends on Axis clock DT bindings, `sys_refclk`, optional `i2s_refclk` and fractional clocks, and the common clock onecell provider interface. The AMBA APB clock comment explains why some clocks must be available early.

Risks and test signals: Risks include global state assumptions, `BUG_ON()` if syscon mapping fails, optional I2S parent handling, and unregistered clocks left as `-EPROBE_DEFER`. Tests should verify ARTPEC-6 boot, UART/SPI early clocks, I2S parent selection, provider indices from `axis,artpec6-clkctrl.h`, and no unexpected clock registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axis/clk-artpec6.c -->
