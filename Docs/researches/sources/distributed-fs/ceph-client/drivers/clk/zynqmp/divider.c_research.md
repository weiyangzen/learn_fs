# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/divider.c

Purpose: implements ZynqMP firmware-controlled adjustable divider clocks, including read-only, power-of-two, and fractional-parent cases.

Important APIs/types/functions: `struct zynqmp_clk_divider`, `zynqmp_clk_register_divider()`, `zynqmp_clk_divider_recalc_rate()`, `zynqmp_clk_divider_determine_rate()`, `zynqmp_clk_divider_set_rate()`, `zynqmp_clk_get_max_divisor()`, and divider flag mapping helpers.

Control flow: registration decodes topology flags, asks firmware for the maximum divisor, and registers either read-write or read-only CCF ops. Recalc reads packed DIV1/DIV2 values via `zynqmp_pm_clock_getdivider()`. Set-rate computes the closest divisor and writes it through `zynqmp_pm_clock_setdivider()`.

State and persistence: hardware divider state persists in firmware. The driver stores the clock id, divider type, max divisor, and decoded behavior flags.

Dependencies and integration points: used by `clkc.c` for `TYPE_DIV1` and `TYPE_DIV2` nodes. Depends on generic divider helpers, PM clock get/set divider APIs, and CCF rate request semantics.

Risks: read-only selection tests generic `CLK_DIVIDER_READ_ONLY` against firmware `type_flag`. Flag mapping maps `ZYNQMP_CLK_DIVIDER_POWER_OF_TWO` to `CLK_DIVIDER_HIWORD_MASK`, which should be reviewed against intended ABI. Zero divisor handling warns but returns parent rate. Fractional-parent logic mutates `best_parent_rate` when `CLK_SET_RATE_PARENT` is set.

Test signals: rate rounding across max divisor boundaries, DIV1/DIV2 packed writes, read-only divider behavior, power-of-two divider rates, and firmware failures from max-divisor or setdivider queries.
