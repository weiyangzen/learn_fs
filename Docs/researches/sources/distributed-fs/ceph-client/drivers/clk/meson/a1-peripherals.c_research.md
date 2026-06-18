# sources/distributed-fs/ceph-client/drivers/clk/meson/a1-peripherals.c

Purpose: `a1-peripherals.c` is the Amlogic A1 peripherals clock-controller driver. It declares a large static clock tree for system, DSP, RTC, CEC, PWM, SPI, USB, SD/eMMC, PSRAM, DMC, and many peripheral bus gates, then registers it through the Meson MMIO clock-controller helper.

Important APIs and types: the file uses `struct clk_regmap`, `struct clk_fixed_factor`, `struct meson_clk_dualdiv_data`, `struct clk_regmap_mux_data`, `struct clk_regmap_div_data`, and `struct clk_regmap_gate_data`. It exports no public functions; its platform driver is registered with `module_platform_driver(a1_peripherals_clkc_driver)`. The clock provider data is `a1_peripherals_clkc_data` and the onecell array is `a1_peripherals_hw_clks[]`.

Control flow: there is little imperative logic. Probe is delegated to `meson_clkc_mmio_probe`, which uses the OF match data for `"amlogic,a1-peripherals-clkc"`. Static descriptors model the tree: oscillator input gates feed PLL input names; RTC and CEC 32 kHz clocks use dual-divider tables; system A/B clock branches are read-only boot-owned mux/div/gate chains and feed the critical `sys` mux; DSP A/B clocks have selectable mux/div/gate branches; device clocks are expressed as mux/div/gate chains; peripheral PCLK gates are generated through the `A1_PCLK` macro.

State and persistence: all runtime state is common clock framework registration state and the hardware register fields described by offsets such as `SYS_CLK_CTRL0`, `SYS_CLK_EN0`, and device-specific clock control registers. Boot firmware state is preserved for read-only system clocks and critical clocks. There is no persistent storage.

Dependencies and integration points: it depends on Meson `clk-regmap`, `clk-dualdiv`, and `meson-clkc-utils`, plus DT bindings from `amlogic,a1-peripherals-clkc.h`. It consumes external parent clocks by firmware names such as `xtal`, `fclk_div2`, `fclk_div3`, `fclk_div5`, `fclk_div7`, and `hifi_pll`, which are supplied by the A1 PLL controller or fixed firmware clocks.

Risks: the provider array is sparse and indexed by binding IDs; wrong indexes break DT consumers. Several gates use `CLK_IGNORE_UNUSED` for historical reasons, which can hide missing consumers and keep unused hardware active. Read-only system clocks assume boot firmware set safe values. Parent value tables skip unsupported hardware selector values; adding support requires careful binding and mux table updates.

Test signals: boot A1 with both PLL and peripherals controllers and inspect `clk_summary` for all binding IDs. Exercise consumers for UART, I2C, PWM, SPI, USB, SD/eMMC, SARADC, CEC, DSP, PSRAM, and DMC. Check that critical `sys` and fclk-derived clocks are never disabled, and verify rate setting for PWM/SPI/SD/USB mux-div-gate paths.
