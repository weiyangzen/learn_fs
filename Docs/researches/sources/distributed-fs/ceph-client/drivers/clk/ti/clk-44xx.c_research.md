# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-44xx.c

## Purpose

`clk-44xx.c` provides OMAP4 clock-controller metadata, aliases, and default DPLL programming. It describes many OMAP4 clkctrl modules and performs early configuration of the ABE and USB DPLLs.

## Important APIs, Types, And Functions

The file defines default rates `OMAP4_DPLL_ABE_DEFFREQ` and `OMAP4_DPLL_USB_DEFFREQ`. Large `omap_clkctrl_reg_data` and `omap_clkctrl_bit_data` tables describe MPUSS, Tesla/DSP, ABE, L4 AO, L3 main, Ducati/IPU, DMA, EMIF, D2D, L4 CFG, L3 INSTR, IVAHD, ISS, DSS, GPU, L3 INIT, L4 PER, L4 SECURE, and WKUP domains. Bit data models module subclocks as gates, muxes, and dividers for AESS, DMIC, McASP, McBSP, SlimBus, timers, DSS, GPU, MMC, HSI, USB host/OTG/TLL, OCP2SCP, GPIO, McSPI, UART, and security modules.

`omap4_clkctrl_data[]` maps physical clkctrl base addresses to register arrays. `omap44xx_clks[]` provides legacy aliases for audio, display, GPIO debounce, MMC, timers, USB host/TLL/OTG, MCBSP, SlimBus, and other generated clkctrl subclocks. `omap4xxx_dt_clk_init()` performs initialization.

## Control Flow

OMAP4 init registers aliases, disables autoidle, adds aliases, then sets the ABE DPLL reference and bypass muxes to `sys_32k_ck`, programs `dpll_abe_ck` to 98.304 MHz, programs `dpll_abe_m2x2_ck` to 196.608 MHz, programs USB DPLL to 960 MHz, and programs USB M2 to 480 MHz. Errors are logged but do not abort the init function.

## State And Persistence Behavior

Clkctrl tables are init-only metadata. Persistent effects include registered clocks/aliases, disabled autoidle state, ABE DPLL parent selections, ABE and USB DPLL rates, and any module clock state changed by consumers. The DPLL programming is essential after warm reboot and for USB operation.

## Dependencies And Integration Points

The file depends on OMAP4 binding constants, TI clkctrl helpers, DPLL support, autoidle, and CCF. It integrates with OMAP4 audio back end, display, GPU, IPU/Ducati, IVAHD, ISS, USB, MMC, timers, GPIO, I2C, UART, McSPI, SlimBus, McBSP, security accelerators, EMIF, and WKUP peripherals.

## Risks And Edge Cases

The init path logs DPLL setup failures but returns success, so downstream peripheral failures may be the only symptom. Many aliases are generated clkctrl names with register offsets and bit indices; any mismatch breaks legacy consumers. ABE DPLL warm-reboot behavior depends on both reference and bypass muxes using `sys_32k_ck`. USB DPLL rates must remain at preferred TRM values for USB stability.

## Test Signals

Boot OMAP4430/OMAP4460 systems and verify ABE and USB DPLL rates. Inspect `clk_summary` for ABE, DSS, GPU, MMC, USB host/OTG/TLL, and timer generated clocks. Exercise audio, display, USB, MMC, GPIO debounce, timers, I2C/SPI/UART, security modules, and warm reboot paths involving ABE timers.
