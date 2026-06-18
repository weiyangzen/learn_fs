# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-frac.c

Purpose: Implements an adjustable MXS fractional divider with a busy bit. It is used for clocks such as SAIF where the output is `parent_rate * div / 2^width`.

Important APIs, types, and functions: `struct clk_frac` stores `clk_hw`, register, shift, width, and busy bit. `mxs_clk_frac()` registers the clock with `clk_frac_ops`. `clk_frac_recalc_rate()` reads the fractional field and computes the scaled rate. `clk_frac_determine_rate()` and `clk_frac_set_rate()` calculate a divider from requested and parent rates, reject rates above the parent or zero divisors, and update the register under `mxs_lock`.

Control flow: Consumers request a rate through CCF. The determine path adjusts `req->rate` to the rounded achievable value. The set path writes the fraction field and waits for the busy bit via `mxs_clk_wait()`.

State and persistence: Fractional divider state is stored in MMIO. The allocated `struct clk_frac` persists after registration. Register writes are serialized by the global MXS spinlock.

Dependencies and integration points: Used by `clk-imx23.c` and `clk-imx28.c` for SAIF divider clocks. Depends on `do_div()` arithmetic, relaxed IO accessors, CCF rate request semantics, and `mxs_clk_wait()`.

Risks: `(1 << width)` assumes width values small enough for 32-bit shifts. Very low requested rates can compute zero and fail with `-EINVAL`. Rounding behavior increments `req->rate` if the computed result truncates, so rate expectations should account for upward rounding.

Test signals: SAIF rate tests should exercise valid rates below the parent, rate-above-parent rejection, zero-divider rejection, and timeout behavior when the busy bit remains set. Debugfs should show the rounded rate after `set_rate`.
