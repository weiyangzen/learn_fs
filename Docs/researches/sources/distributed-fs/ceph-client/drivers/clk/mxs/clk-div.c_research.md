# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-div.c

Purpose: Defines an MXS integer divider clock wrapper around the generic `clk_divider` implementation, adding hardware busy-bit polling after rate changes.

Important APIs, types, and functions: `struct clk_div` embeds `struct clk_divider`, stores the generic divider ops pointer, the divider register, and the busy bit. `mxs_clk_div()` allocates and registers the clock with `CLK_DIVIDER_ONE_BASED` and `CLK_SET_RATE_PARENT`. `clk_div_recalc_rate()`, `clk_div_determine_rate()`, and `clk_div_set_rate()` delegate to generic divider ops, then call `mxs_clk_wait()` on successful writes.

Control flow: SoC topology files call `mxs_clk_div(name, parent, reg, shift, width, busy)`. CCF invokes wrapper ops. On `set_rate`, the generic divider updates the register under `mxs_lock`; the wrapper waits until the provided busy bit clears.

State and persistence: One allocated `struct clk_div` persists per clock. The actual divider state is MMIO-backed. The shared `mxs_lock` serializes register updates.

Dependencies and integration points: Depends on `clk.h` for `mxs_clk_wait()` and `mxs_lock`, the generic CCF divider ops, and SoC files passing correct register and busy-bit metadata.

Risks: Incorrect busy-bit metadata can cause false success, timeout, or indefinite hardware instability. Width/shift combinations are not validated beyond generic helpers. Allocation is not devm-managed because these clocks are early platform clocks.

Test signals: Rate-change tests should confirm the register field changes, the busy bit clears within 10 ms, and callers receive `-ETIMEDOUT` on stuck hardware. `clk_summary` should show derived divider rates for CPU, HBUS, XBUS, SSP, GPMI, EMI, LCDIF, and ETM paths.
