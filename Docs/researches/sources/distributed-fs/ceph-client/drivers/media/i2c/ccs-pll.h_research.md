# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs-pll.h

Purpose: Public data contract for the generic CCS/SMIA PLL calculator.

Important APIs/types/functions: Defines bus types `CCS_PLL_BUS_TYPE_CSI2_DPHY` and `CCS_PLL_BUS_TYPE_CSI2_CPHY`, calculation flags such as `CCS_PLL_FLAG_LANE_SPEED_MODEL`, `CCS_PLL_FLAG_DUAL_PLL`, `CCS_PLL_FLAG_NO_OP_CLOCKS`, `CCS_PLL_FLAG_FLEXIBLE_OP_PIX_CLK_DIV`, FIFO rate flags, and OP DDR flags. `struct ccs_pll_branch_fr` and `struct ccs_pll_branch_bk` represent front-end PLL and back-end sys/pix dividers. `struct ccs_pll` contains input bus/lane/binning/scaling/bpp/link/extclk fields plus calculated VT/OP branches and pixel rates. `struct ccs_pll_limits` nests front/back branch limits and line-length limits. `ccs_pll_calculate()` is the exported function.

Control flow: No executable logic. The header describes how callers must populate input fields and limits before calculation and which output fields become valid after success.

State/persistence: No local state. All persistence is caller-owned in `struct ccs_pll` and sensor-specific limits.

Dependencies/integration: Includes `linux/bits.h` for flag definitions and forward declares `struct device` for the calculator logging argument. Included by `ccs-pll.c` and sensor drivers using the helper.

Risks: The flag matrix is dense; invalid combinations can produce `-EINVAL` or surprising pixel rates. Units are encoded only in field names, so callers must consistently use Hz, lane counts, scaling ratios, and bit depths. `flags` is `u16`, leaving limited room for future expansion.

Test signals: Compile-time users should initialize all mandatory input and limit fields. Runtime calculator tests should verify that every flag documented here has at least one passing and one rejecting scenario.
