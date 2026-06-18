# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-7xx.c

Purpose: DRA7/DRA72/DRA74/DRA76 clock initialization data for the OMAP/TI common clock framework. The file is almost entirely `__initconst` metadata that maps PRCM clkctrl register blocks to module clocks and their subclocks, plus `dra7xx_dt_clk_init()` for early clock alias registration and fixed boot-time DPLL programming.

Important APIs/types/functions: it exports `dra7_clkctrl_data[]` for `clkctrl.c` lookup and defines `dra7xx_dt_clk_init()`. It uses `struct omap_clkctrl_data`, `struct omap_clkctrl_reg_data`, `struct omap_clkctrl_bit_data`, and `struct omap_clkctrl_div_data` from `clock.h`; `DT_CLK()` entries form legacy clkdev aliases for generated clkctrl names such as `l4per-clkctrl:0118:24`.

Control flow: `clkctrl.c` selects `dra7_clkctrl_data[]` by machine compatible and clkctrl base address, then iterates register entries. Register entries create a main module clock and optional gate/mux/divider subclocks for timers, UARTs, McASP, MMC, DSS, GMAC, QSPI, PCIe, ATL, GPIO debounce clocks, and other DRA7 domains. `dra7xx_dt_clk_init()` registers aliases, disables autoidle globally, adds fixed/simple aliases, sets GMAC and USB DPLL rates, sets USB M2 to half rate, and enables `dss_deshdcp_clk`.

State and persistence: static tables disappear after init; persistent state is in registered CCF clocks and hardware PRCM/DPLL registers. The initializer programs live DPLL rates and enables one DSS-related clock without releasing it.

Dependencies/integration: depends on `dt-bindings/clock/dra7.h`, CCF, clkdev aliases, TI clkctrl registration, and parent clock names created by DTS/other TI clock files. SoC flags (`CLKF_SOC_DRA72`, `CLKF_SOC_DRA74`, `CLKF_SOC_DRA76`, `CLKF_SOC_NONSEC`) gate entries for SKU/security variants.

Risks: correctness is table driven, so wrong offsets, bit positions, parent names, or SoC masks silently create broken clocks. Boot-time `clk_get_sys()` results are not checked with `IS_ERR()` before `clk_set_rate()`/`clk_prepare_enable()`, relying on complete clock data. DPLL rate programming failures are logged but initialization returns only the last `rc`.

Test signals: boot DRA7-family kernels with clk debug enabled, verify no "failed to lookup clock node" or DPLL setup errors, inspect `/sys/kernel/debug/clk/clk_summary`, exercise MMC/UART/timer/USB/GMAC/DSS/ATL peripherals, and validate DT bindings produce matching clkctrl node names and two-argument clkctrl phandles.
