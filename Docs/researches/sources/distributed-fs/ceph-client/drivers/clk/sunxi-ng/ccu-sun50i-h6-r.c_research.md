# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6-r.c

Purpose: PRCM/R_CCU clock and reset driver for Allwinner H6 and H616 always-on domain clocks. It exposes AR100/R-AHB/R-APB roots, low-speed peripheral gates, IR/1-wire module clocks, and reset lines.

Important APIs, types, and functions: defines `ar100_clk`, `r_apb1_clk`, `r_apb2_clk`, fixed `r_ahb_clk`, APB gate clocks, `ir_clk`, and `w1_clk`. SoC-specific export tables are `sun50i_h6_r_hw_clks` and `sun50i_h616_r_hw_clks`; reset sets are `sun50i_h6_r_ccu_resets` and `sun50i_h616_r_ccu_resets`. `sun50i_h6_r_ccu_probe()` uses OF match data to select a descriptor.

Control flow: platform probe reads `.data` from the matching compatible, maps the MMIO resource, and passes the selected `sunxi_ccu_desc` to `devm_sunxi_ccu_probe()`. No additional register fixups are performed.

State and persistence: state lives in R_CCU MMIO gate/divider/mux/reset bits. The H6 and H616 variants share the same `ccu_common` objects but publish different onecell IDs and reset maps.

Dependencies and integration points: binds `allwinner,sun50i-h6-r-ccu` and `allwinner,sun50i-h616-r-ccu`, integrates with the Sunxi CCU framework, and supplies clocks for RTC/PIO-adjacent always-on peripherals, IR, RSB/I2C/UART, PWM/TWD/timer, and low-power firmware blocks.

Risks and test signals: several parent and divider definitions are derived from BSP/manual interpretation, so mis-modeling affects low-speed peripherals. Sharing common clock objects across variants requires the exported ID tables to hide unsupported clocks correctly. Test with DT lookup on both SoCs, IR receive rate checks, RSB/I2C function, RTC clock retention, and reset control assertions.
