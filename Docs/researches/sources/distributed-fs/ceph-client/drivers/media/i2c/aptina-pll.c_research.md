# sources/distributed-fs/ceph-client/drivers/media/i2c/aptina-pll.c

Purpose: Shared helper that calculates valid Aptina sensor PLL divisors for a requested external clock and pixel clock. It exports `aptina_pll_calculate()` for sensor drivers that need `N`, `M`, and `P1` values within device-specific limits.

Important APIs/types/functions: `aptina_pll_calculate(struct device *dev, const struct aptina_pll_limits *limits, struct aptina_pll *pll)` validates input clocks, derives the reduced multiplier/divisor ratio using `gcd()`, computes a valid multiplier factor range, then searches even `P1` divisors from high to low. The selected result is written back to `pll->n`, `pll->m`, and `pll->p1`; the symbol is exported with `EXPORT_SYMBOL_GPL`.

Control flow: The function first rejects external clocks outside `[ext_clock_min, ext_clock_max]` and zero or too-high pixel clocks. It reduces `pix_clock / ext_clock` to base `m` and combined `n * p1` divisor. It derives `mf_min` and `mf_max` from multiplier, output clock, and combined divisor limits. For each even `p1`, it computes the compatible multiplier-factor increment, intersects that with internal clock limits, and accepts the first non-empty range.

State/persistence: Stateless helper. It mutates only the caller-provided `struct aptina_pll`; no hardware, global state, or persistent memory is touched.

Dependencies/integration: Uses `linux/gcd.h`, `DIV_ROUND_UP`, `roundup`, `dev_dbg()`, and `dev_err()`. It integrates through `aptina-pll.h` and is loaded as a GPL module helper for media sensor drivers.

Risks: Several arithmetic expressions multiply clock frequencies and divisors in `unsigned int`, so high limit values can overflow before division. `p1_min == 0` is explicitly rejected, but other zero limits can still create divide-by-zero hazards if callers provide malformed limits. The search prefers the highest even `P1` and lower acceptable multiplier factor, which may not optimize jitter or power for every sensor.

Test signals: Unit-style tests should feed known Aptina clock tables and verify exact `N/M/P1` results, boundary rejection for invalid ext/pixel clocks, no valid-divisor cases, and low/high internal/output clock limits. Dynamic debug logs should show the selected factors.
