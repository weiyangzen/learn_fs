## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-fracn-gppll.c

### Purpose
`clk-fracn-gppll.c` implements i.MX fractional-N general-purpose PLLs and integer-only variants using table-driven supported rates.

### Important APIs, Types, And Functions
The exported templates `imx_fracn_gppll` and `imx_fracn_gppll_integer` provide rate tables. `struct clk_fracn_gppll` stores base, rate table, count, and flags. Important functions include `imx_get_pll_settings()`, `clk_fracn_gppll_determine_rate()`, `clk_fracn_gppll_recalc_rate()`, `clk_fracn_gppll_set_rate()`, prepare/unprepare ops, and constructors `imx_clk_fracn_gppll()`/`imx_clk_fracn_gppll_integer()`.

### Control Flow
Determine-rate selects the first table entry not above the request, assuming descending tables. Set-rate finds exact settings, disables hardware control/output, powers down, disables bypass, writes divider and fraction fields, waits 5 us, powers up, waits for lock, enables output, and warns if analog MFN status differs. Prepare powers up with bypass then enables output and clears bypass.

### State, Persistence, And Dependencies
PLL state persists across control, divider, numerator, denominator, and status registers. Driver state stores immutable rate-table pointers. Dependencies include bitfield helpers, CCF, I/O polling, and precise PLL register semantics.

### Integration Points
Newer i.MX SoC clock trees use these PLLs as roots for bus, media, and peripheral clocks. Table exports let SoC files choose fractional or integer sets.

### Risks
`clk_fracn_gppll_set_rate()` does not check `imx_get_pll_settings()` for NULL before dereferencing, so unsupported direct set requests can crash. Integer recalc path divides by `mfd` only in fractional mode, but fraction tables must avoid invalid denominators. Lock timeout is short and hardware-dependent.

### Test Signals
Set every table rate, request unsupported rates through CCF and direct set paths, validate recalc table matching, force lock timeout, and check prepare/unprepare power sequencing.
