# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-2xxx.c

## Purpose

`clk-2xxx.c` performs clock alias registration and early initialization for OMAP2420 and OMAP2430 SoCs. It maps legacy device/connection names to DT clock names, initializes OMAP2 clock type voltage/processor scaling support, disables autoidle, enables required early clocks, and logs the main clock rates.

## Important APIs, Types, And Functions

`omap2xxx_clks[]` is the common alias table for OMAP2, covering fixed clocks, APLLs, DPLL/core/MPU/DSP/GFX clocks, DSS, timers, MCBSP, McSPI, UART, GPIO, watchdog, I2C, crypto, USB, and timer parent aliases. `omap2420_clks[]` and `omap2430_clks[]` add SoC-specific aliases. `enable_init_clks[]` lists clocks kept enabled during init: APLL96, APLL54, sync 32k, omapctrl, GPMC, and SDRC. `omap2xxx_dt_clk_init()` performs common initialization, while `omap2420_dt_clk_init()` and `omap2430_dt_clk_init()` select the SoC-specific table.

## Control Flow

The SoC-specific init function calls `omap2xxx_dt_clk_init()` with a selector. Common aliases are registered first, then OMAP2420 or OMAP2430 aliases. `omap2xxx_clkt_vps_init()` initializes clock-type behavior, autoidle is disabled globally, required init clocks are enabled, and an informational crystal/DPLL/MPU rate line is printed using `clk_get_sys()` and `clk_get_rate()`.

## State And Persistence Behavior

The persistent software state is CCF alias registration and enabled init clocks. Hardware PRCM state changes when autoidle is disabled and the init clocks are prepared/enabled. The file does not store private mutable state after init.

## Dependencies And Integration Points

It depends on TI DT clock registration helpers, OMAP2 clock-type support, autoidle support, and the legacy consumer naming expected by OMAP platform devices. It integrates with board DT data that defines the underlying clock nodes referenced by the alias names.

## Risks And Edge Cases

Alias names are compatibility-sensitive. Removing or renaming entries can break older platform devices that still request clocks by legacy con_id/dev_id. Missing base clocks cause rate logging or init-clock enables to fail. The init sequence assumes autoidle should be disabled before enabling critical boot clocks.

## Test Signals

Boot OMAP2420 and OMAP2430 DT systems and verify the crystal/DPLL/MPU rate line. Check that legacy consumers such as timers, I2C, McSPI, MCBSP, DSS, USB, watchdog, crypto, and MMC obtain clocks. Confirm listed init clocks remain enabled and that autoidle disable does not regress suspend/resume expectations.
