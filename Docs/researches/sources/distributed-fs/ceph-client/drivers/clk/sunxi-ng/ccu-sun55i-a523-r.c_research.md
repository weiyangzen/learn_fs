# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-r.c

Purpose: PRCM/R-domain CCU driver for Allwinner A523. It models always-on bus roots, timers, PWM, SPI, spinlock/message-box, UART/I2C, PPU, IR, DMA, RTC, CPU configuration gates, and resets.

Important APIs, types, and functions: defines parent-data arrays for `hosc`, `losc`, `iosc`, `pll-periph`, `pll-audio`, and named 300 MHz PLL derivatives. Core clocks are `r_ahb_clk`, `r_apb0_clk`, `r_apb1_clk`, timer clocks, `r_pwmctrl_clk`, `r_spi_clk`, `r_ir_rx_clk`, many `SUNXI_CCU_GATE_HW` bus gates, `sun55i_a523_r_hw_clks`, `sun55i_a523_r_ccu_resets`, `sun55i_a523_r_ccu_desc`, and `sun55i_a523_r_ccu_probe()`.

Control flow: probe maps the R_CCU MMIO resource and registers the static descriptor with `devm_sunxi_ccu_probe()`. There are no probe-time register fixups.

State and persistence: state is hardware mux/divider/gate/reset bits. Critical gates for R DMA and CPUCFG are marked `CLK_IS_CRITICAL` to keep always-on infrastructure available. Software state is static plus devm registration.

Dependencies and integration points: binds `allwinner,sun55i-a523-r-ccu`, depends on main PLL providers by firmware/name parent references, and provides low-power clocks/resets to R-domain peripherals and MCU-domain parents (`r-ahb`, `r-apb0`).

Risks and test signals: parent-name spelling is sensitive (`pll-periph0-300M`/`pll-periph1-300M` names must match providers). Critical flag choices affect power management. Reset array ordering includes PPU0 after CPUCFG but indexed by binding IDs, so ID validation matters. Test with R UART/I2C/SPI/IR operation, RTC, wake-capable peripherals, MCU CCU probe, reset-controller consumers, and clk summary parent resolution.
