# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2044-pll.c

## Purpose
This file is the SG2044 PLL clock-controller driver. It registers FPLL, DPLL, and MPLL clocks backed by a parent syscon regmap, exposes them through a platform-device ID table, and supports rate changes for MPLLs while registering FPLLs/DPLLs as read-only.

## Important APIs, Types, And Functions
Important structs are `sg2044_pll_limit`, `sg2044_pll_internal`, `sg2044_clk_common`, `sg2044_pll`, `sg2044_pll_desc_data`, and `sg2044_pll_ctrl`. Rate helpers include `sg2044_pll_calc_vco_rate()`, `sg2044_pll_calc_rate()`, `sg2044_pll_recalc_rate()`, `sg2042_pll_compute_postdiv()` (name appears inherited from SG2042), `sg2044_compute_pll_setting()`, `sg2044_pll_determine_rate()`, `sg2044_pll_poll_update()`, `sg2044_pll_enable()`, `sg2044_pll_update_vcosel()`, and `sg2044_pll_set_rate()`.

Macros `DEFINE_SG2044_PLL()` and `DEFINE_SG2044_PLL_RO()` declare writable and read-only PLLs. The static table includes three FPLLs, eight DPLLs, and six MPLLs. `sg2044_pll_init_ctrl()` initializes common state and registers all PLLs.

## Control Flow
Probe retrieves the parent device's syscon regmap with `device_node_to_regmap()`, gets descriptor data from `platform_get_device_id()`, allocates onecell storage, and registers each PLL. Set-rate clamps/searches valid PLL parameters, computes VCO rate, adds calibration/update bits, takes the shared lock with cleanup guards, disables the PLL, updates VCO select, writes high-control fields, and re-enables the PLL after lock polling.

## State And Persistence
Runtime state is the regmap pointer, shared lock, onecell provider, and each PLL's syscon offset. Hardware state persists in syscon PLL control, status, and enable registers under `SG2044_SYSCON_PLL_OFFSET`. Read-only FPLL/DPLL clocks still report rates from hardware fields.

## Dependencies And Integration Points
The driver depends on `MFD_SYSCON`, `REGMAP_MMIO`, CCF, cleanup guard macros, and dt-binding IDs from `sophgo,sg2044-pll.h`. The main SG2044 clock controller consumes firmware parent names such as `fpll0`, `dpll0`, and `mpll0`.

## Risks
The helper named `sg2042_pll_compute_postdiv()` in an SG2044 driver is confusing and can mislead maintenance, though functionally local. `sg2044_pll_set_rate()` ignores the return value from `sg2044_pll_update_vcosel()` and the final enable call is not stored in `ret`, so failures can be missed. Read-only PLLs only expose recalculation, not determine-rate, which may affect consumers asking for rounded rates. The platform-device ID path requires an MFD child named `sg2044-pll`; OF matching is not used directly.

## Test Signals
Probe tests must validate parent syscon child creation and provider registration. Rate tests should cover MPLL set-rate at boundaries, VCO select threshold near 2.4 GHz, and lock timeout behavior. Main SG2044 clock consumers should resolve all PLL firmware names.
