# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-54xx.c

## Purpose

`clk-54xx.c` provides OMAP5 clock-controller metadata, aliases, and default DPLL programming. It is the OMAP5 counterpart to the OMAP4 clock init file, with updated clkctrl domains and generated subclock aliases for OMAP54xx devices.

## Important APIs, Types, And Functions

The file defines `OMAP5_DPLL_ABE_DEFFREQ` at 98.304 MHz and `OMAP5_DPLL_USB_DEFFREQ` at 960 MHz. `omap_clkctrl_reg_data` and `omap_clkctrl_bit_data` arrays describe MPU, DSP, ABE, L3 main, IPU, DMA, EMIF, L4 CFG, L3 INSTR, L4 PER, L4 SECURE, IVA, DSS, GPU, L3 INIT, and WKUPAON domains. Bit data describes AESS divider, DMIC/McBSP sync muxes, timers, GPIO debounce clocks, DSS gates, GPU mux/divider bits, MMC mux/dividers, USB host/TLL gates and muxes, SATA refclk, USB OTG SS refclk, GPIO1 debounce, and timer1 mux.

`omap5_clkctrl_data[]` maps OMAP5 PRCM base addresses to these arrays. `omap54xx_clks[]` aliases generated clkctrl names for timers, audio, DSS, GPIO debounce, MCBSP, MMC, SATA, USB, and UTMI clocks. `omap5xxx_dt_clk_init()` performs init-time registration and DPLL programming.

## Control Flow

OMAP5 init registers aliases, disables autoidle, adds aliases, sets ABE DPLL reference and bypass muxes to `sys_32k_ck`, programs `dpll_abe_ck` and `dpll_abe_m2x2_ck`, programs USB DPLL and USB M2, and logs errors if any step fails. The function returns zero regardless of logged configuration errors.

## State And Persistence Behavior

The clkctrl metadata is init-only. Persistent state includes clock aliases, disabled autoidle, ABE mux parent choices, ABE DPLL rate, ABE M2x2 rate, USB DPLL rate, and USB M2 rate. Runtime module clock state is then managed by CCF consumers through clkctrl-generated clocks.

## Dependencies And Integration Points

The file depends on OMAP5 binding constants, TI clkctrl support, DPLL helpers, autoidle, and CCF. It integrates with OMAP5 DSP, ABE/audio, IPU, EMIF, DSS, GPU, MMC, USB host/TLL/OTG SS, SATA, timers, GPIO, I2C, McSPI, UART, security accelerators, DMA, and WKUPAON peripherals.

## Risks And Edge Cases

As with OMAP4, DPLL configuration errors are logged but not returned. Generated clkctrl aliases must match DT clock names and register bit positions exactly. ABE warm-reboot stability relies on both ABE reference and bypass muxes using `sys_32k_ck`. USB and SATA peripheral stability depends on correct high-frequency reference clock parents and DPLL rates.

## Test Signals

Boot OMAP5 hardware and verify ABE/USB DPLL rates and parent muxes. Inspect `clk_summary` for generated OMAP5 clkctrl clocks. Exercise audio, MCBSP, DSS/display, GPU, MMC, USB host/TLL/OTG SS, SATA, GPIO debounce, timers, I2C/SPI/UART, security modules, and warm reboot.
