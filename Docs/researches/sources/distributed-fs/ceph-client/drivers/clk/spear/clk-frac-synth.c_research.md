# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-frac-synth.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-frac-synth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-frac-synth.c

Purpose: implements SPEAr fractional synthesizer clocks using a 17-bit divider value programmed from a rate table.

Important APIs and control flow: `frac_calc_rate()` calculates `Fin / (2 * div)` using fixed scaling to preserve fractional precision. `clk_frac_determine_rate()` chooses the nearest supported table row with `clk_round_rate_index()`. `clk_frac_recalc_rate()` reads the divider field, returns zero for a zero divider, and computes the current rate. `clk_frac_set_rate()` rewrites the divider field for the selected row. `clk_register_frac()` allocates and registers the CCF clock with one parent.

State and persistence behavior: persistent hardware state is the 17-bit divider field. Software state is an allocated `struct clk_frac` with register pointer, table, count, and optional lock; it is not devm-managed here.

Dependencies and integration points: depends on CCF, raw MMIO, optional shared spinlocks, the shared SPEAr table-rounding helper, and `struct frac_rate_tbl`. SPEAr1310/1340 use this for CLCD, generic synthesizers, and SPEAr1340 system/AMBA synthesizers.

Risks and test signals: risks include NULL return on register failure instead of preserving precise error codes, no unregister path, rate-table ordering assumptions, arithmetic truncation at 10 kHz scale, and invalid zero dividers producing zero rates. Test signals include `clk_round_rate()` and `clk_set_rate()` selecting expected divider rows, CLCD/system/AMBA clocks matching hardware rates, and no register corruption when multiple clocks share the same spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-frac-synth.c -->
