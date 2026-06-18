# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-3xxx.c

## Purpose

`clk-3xxx.c` provides OMAP3/AM35xx clock initialization and special clock hardware operations. It handles ES-specific SSI/DSS/USBHOST/HSOTGUSB idlest bit locations, AM35xx IPSS companion/ack logic, aliases for OMAP3 variants, DPLL5 USB erratum programming, and early init sequencing.

## Important APIs, Types, And Functions

The file exports several `clk_hw_omap_ops`: `clkhwops_omap3430es2_iclk_ssi_wait`, `clkhwops_omap3430es2_dss_usbhost_wait`, `clkhwops_omap3430es2_iclk_dss_usbhost_wait`, `clkhwops_omap3430es2_iclk_hsotgusb_wait`, `clkhwops_am35xx_ipss_module_wait`, and `clkhwops_am35xx_ipss_wait`. Their `find_idlest` and `find_companion` callbacks adjust register offsets and bit positions where default OMAP logic does not match hardware.

Alias tables cover common OMAP3 timer aliases, OMAP3430 ES1/ES2 SSI and USB clock names, AM35xx clocks, and DSS variants. `omap3_clk_lock_dpll5()` programs DPLL5 and its M2 divider for the USB host clock drift erratum. `omap3xxx_dt_clk_init()` performs variant-specific registration and common initialization.

## Control Flow

Variant init functions call `omap3xxx_dt_clk_init()` with a SoC selector. The common function registers base and variant alias tables, disables autoidle, adds aliases, enables `sdrc_ick`, `gpmc_fck`, and `omapctrl_ick`, prints oscillator/core/MPU rates, and locks DPLL5 for all but OMAP3430 ES1. Runtime enable paths using the exported hwops call the custom idlest/companion callbacks while waiting for module clocks.

## State And Persistence Behavior

Alias registrations and init clock enables persist in CCF state. DPLL5 programming persists in hardware registers and is required for stable USB host operation. The exported `clk_hw_omap_ops` are static const behavior tables used by clock definitions elsewhere.

## Dependencies And Integration Points

The file depends on `clock.h`, TI/OMAP clock helpers, OMAP3 DPLL definitions, autoidle, and CCF. It integrates with SSI, DSS, USBHOST, HSOTGUSB, AM35xx IPSS, SDRC, GPMC, omapctrl, timers, and variant-specific DT clock data.

## Risks And Edge Cases

Hardware idlest bit shifts differ by module and chip revision; using default wait ops can hang enables or skip needed waits. `omap3_clk_lock_dpll5()` does not check `clk_get()` errors before setting rates and preparing clocks. The USB erratum frequency must stay aligned with DPLL implementation expectations because DPLL rate handlers detect the special frequency.

## Test Signals

Boot OMAP3430 ES1, OMAP3430 ES2+, OMAP3630, and AM35xx variants where possible. Exercise SSI, DSS, USB host, HSOTGUSB, and AM35xx IPSS peripherals while checking module enable waits. Verify DPLL5 and DPLL5_M2 rates for USB host and inspect boot rate logging.
