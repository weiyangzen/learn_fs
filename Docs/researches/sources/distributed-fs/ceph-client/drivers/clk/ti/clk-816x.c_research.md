# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-816x.c

Purpose: DM816x/TI81xx clkctrl metadata and boot-time legacy alias setup. The file maps default and always-on PRCM clock-control registers to parent clocks and declares a few clock aliases expected by timer and legacy platform code.

Important APIs/types/functions: exports `dm816_clkctrl_data[]`; defines `dm816x_dt_clk_init()`. Uses `omap_clkctrl_reg_data`, `ti_dt_clk`, `DT_CLK()`, and `omap2_clk_enable_init_clocks()`.

Control flow: clkctrl metadata is consumed by `clkctrl.c` when the machine compatible is `ti,dm816`. `dm816x_dt_clk_init()` registers aliases for system and timer clocks, disables autoidle, adds simple aliases, and enables DDR PLL outputs plus `sysclk6_ck`.

State and persistence: source tables are init-only; enabled init clocks and PRCM module state persist. No private runtime structure is allocated here.

Dependencies/integration: depends on `dt-bindings/clock/dm816.h`, CCF, TI clkctrl common code, and clock providers for `ddr_pll_clk1/2/3`, `sysclk6_ck`, and sysclk/timer parents.

Risks: all module access relies on correct parent clock names and register offsets. `CLKF_NO_IDLEST` on watchdog, RTC, MDIO, and EMAC avoids waiting for idle status; incorrect use would hide readiness failures or cause timeouts if removed.

Test signals: boot DM816x, inspect clk summary for sysclk aliases, verify USB/UART/GPIO/I2C/timer/MMC/GPMC/EMAC module clock enable paths, and watch for init-clock warnings during boot.
