# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-43xx.c

## Purpose

`clk-43xx.c` defines AM43xx and AM438x clkctrl metadata, clock aliases, and initialization fixups. It describes AM4 PRCM domains and sets the CPSW CPTS reference clock parent for stable PTP operation.

## Important APIs, Types, And Functions

The file declares clkctrl register arrays for L3S TSC, L4 WKUP AON, L4 WKUP, MPU, GFX L3, RTC, L3, L3S, PRUSS OCP, L4LS, EMIF, DSS, and CPSW 125 MHz domains. Bit-data arrays describe counter 32K, GPIO debounce gates, and USB OTG SS refclk gates. `am4_clkctrl_data[]` covers the full AM43xx set, while `am438x_clkctrl_data[]` omits RTC-related blocks for AM438x. `am43xx_clks[]` provides legacy aliases for timers, GPIO debounce clocks, synctimer, and USB refclks. `enable_init_clks[]` keeps L3 main enabled for suspend.

## Control Flow

`am43xx_dt_clk_init()` registers aliases, disables autoidle, enables the init clocks, adds aliases, and then changes `cpsw_cpts_rft_clk` parent to `dpll_core_m5_ck` because the default `dpll_core_m4_ck` causes PTP clockcheck errors.

## State And Persistence Behavior

The clkctrl descriptions are init-only. Persistent state includes registered CCF clocks/aliases, disabled autoidle state, enabled L3 main clock, and the hardware mux parent selection for `cpsw_cpts_rft_clk`.

## Dependencies And Integration Points

The file depends on AM4 binding constants, TI clkctrl helpers, OMAP autoidle, and CCF legacy lookup. It integrates with AM43xx peripherals including ADC/TSC, WKUP M3, MPU, GFX, RTC, AES/DES/SHA/TPCC/TPTC, USB OTG SS, PRUSS, GPIO, DCAN, EPWMSS, ELM, HDQ, I2C, mailbox, MMC, RNG, SPI, timers, UART, OCP2SCP, EMIF, DSS, and CPSW.

## Risks And Edge Cases

The CPTS parent fixup assumes both named clocks are registered; missing aliases can break PTP setup. AM43xx and AM438x clkctrl data differ, so using the wrong table can expose nonexistent RTC blocks or omit needed clocks. `CLKF_NO_IDLEST` and `CLKF_SW_SUP` flags encode hardware behavior and should not be changed without TRM validation.

## Test Signals

Boot AM43xx and AM438x DTs and verify clkctrl coverage. Exercise CPSW PTP and confirm no clockcheck regressions. Test USB OTG SS, GPIO debounce, timers, UART/I2C/SPI/MMC, PRUSS, DSS, and suspend/resume with L3 main retained.
