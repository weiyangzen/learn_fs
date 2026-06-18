# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-agilex.c

Purpose: descriptor tables and platform driver for Intel Agilex and N5X clock managers.

Important APIs/types/functions: parent-data mux arrays; `agilex_pll_clks`; N5X and Agilex peripheral counter tables; Agilex gate table; registration loops; `agilex_clkmgr_init()`, `n5x_clkmgr_init()`, and `agilex_clkmgr_probe()`.

Control flow: probe dispatches by OF match to Agilex or N5X init. Init maps MMIO, allocates `stratix10_clock_data`, initializes slots to `ERR_PTR(-ENOENT)`, registers PLLs, counter outputs, peripheral counters, and gates, then adds an OF onecell provider.

State and persistence behavior: per-device base and onecell clock data; hardware registers hold rate/parent/gate/bypass state; no PM save state.

Dependencies/integration points: `stratix10-clk.h`, helper files `clk-pll-s10.c`, `clk-periph-s10.c`, `clk-gate-s10.c`, CCF, platform/OF APIs, and Agilex DT binding IDs.

Risks: per-clock failures log and continue; parent-data names must match firmware; N5X uses different rate helpers while sharing tables; provider add return is unchecked.

Test signals: boot Agilex/N5X, verify onecell IDs, compare PLL rates, inspect EMAC/SDMMC/GPIO bypass parents, and confirm critical clocks stay enabled.
