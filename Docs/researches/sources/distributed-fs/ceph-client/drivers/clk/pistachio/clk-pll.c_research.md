# sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk-pll.c

Purpose: Implements Pistachio PLL clocks for GF40LP fractional and low-area integer PLL types, with optional table-driven rate programming and fixed-rate recalc-only variants.

Important APIs, types, and functions: `struct pistachio_clk_pll` stores `clk_hw`, base, rate table, and rate count. `pll_register()` selects ops based on `enum pistachio_pll_type` and whether a rate table exists. Fractional ops manage `PLL_CTRL3/4`, mode selection, fractional fields, and recalc. Low-area integer ops manage `PLL_CTRL1/2` integer fields. `pistachio_clk_register_pll()` registers descriptor arrays into a provider.

Control flow: Enable clears power-down and bypass bits, then spins in `pll_lock()` until lock. Set-rate looks up exact table parameters, validates/warns for VCO and PFD constraints, writes divider fields, switches fractional/int mode where applicable, and relocks if already enabled. Determine-rate picks a table entry not exceeding the requested rate, defaulting to the first entry.

State and persistence: Per-PLL objects persist after registration. Rate configuration and power state persist in MMIO. Fixed PLL descriptors with no rate table expose enable/disable/recalc but no set-rate.

Dependencies and integration points: Used by `clk-pistachio.c`. Depends on table definitions in `struct pistachio_pll`, CCF, and hardware lock bit behavior.

Risks: `pll_lock()` has no timeout and can spin forever if the PLL never locks. Set-rate requires an exact rate-table match and warns, rather than fails, on several hardware constraint violations. Changing postdiv values while enabled is only warned about, not prevented.

Test signals: Recalc should match register encodings for both PLL types. Fault injection or hardware tests should verify lock behavior. Rate-table PLLs should reject missing parameters with `-EINVAL`; fixed PLLs should not expose set-rate.
