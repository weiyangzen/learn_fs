# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-33xx.c

## Purpose

`clk-33xx.c` defines AM33xx clkctrl metadata, legacy aliases, and clock initialization fixups. It describes PRCM clkctrl register blocks for AM335x-style domains and applies platform-specific parent selections for timers and watchdogs.

## Important APIs, Types, And Functions

The file declares many `omap_clkctrl_reg_data` arrays for L4LS, L3S, L3, L4HS, PRUSS OCP, CPSW 125 MHz, LCDC, 24 MHz, L4 WKUP, L3 AON, WKUP M3, MPU, RTC, GFX L3, and CEFUSE domains. Bit-data arrays describe GPIO debounce gates and debug subsystem mux/divider/gate bits. `am3_clkctrl_data[]` maps physical clkctrl base addresses to these arrays. `am33xx_clks[]` provides legacy aliases for timers, GPIO debounce clocks, debug clocks, STM/trace clocks, and clkdiv32k. `enable_init_clks[]` lists DDR/MPU DPLL outputs, L3/L4 clocks, errata-related debug clock, suspend-needed L3 main, and `clkout2_ck`.

## Control Flow

`am33xx_dt_clk_init()` registers aliases, disables autoidle, adds aliases, enables init clocks, then applies fixups: timer3 and timer6 parents are set to `sys_clkin_ck` because default TCLKIN may be absent; WDT1 parent is set to `clkdiv32k_ick` to avoid inaccurate on-chip 32 kHz RC oscillator behavior.

## State And Persistence Behavior

The clkctrl metadata is `__initconst` and discarded after boot. Persistent effects are registered clocks/aliases and PRCM register state from enabled init clocks and parent selections. The timer and watchdog parent changes persist in hardware mux registers until reset or later clock operations.

## Dependencies And Integration Points

The file depends on AM3 DT binding constants, TI clkctrl helpers, OMAP autoidle, and CCF lookup by legacy names. It integrates with AM33xx peripherals including UART, MMC, ELM, I2C, SPI, timers, RNG, GPIO, DCAN, EPWMSS, GPMC, MCASP, PRUSS, CPSW, LCDC, WKUP, debug, RTC, GFX, and CEFUSE.

## Risks And Edge Cases

The fixup code does not check `clk_get_sys()` return values before `clk_set_parent()`, so missing aliases can produce bad pointer usage depending on CCF behavior. Clkctrl names such as `l3-aon-clkctrl:0000:0` are generated contracts with consumers; typos break aliases and init clocks. Errata-driven always-on clocks must be preserved for suspend and debug stability.

## Test Signals

Boot AM335x/AM33xx DT systems and verify clkctrl registration, timer3/timer6 parent selection, WDT1 parent selection, and `clkout2_ck` availability for external peripherals. Exercise GPIO debounce, UART, MMC, I2C, SPI, DCAN, PRUSS, CPSW, LCDC, RTC, and suspend/resume.
