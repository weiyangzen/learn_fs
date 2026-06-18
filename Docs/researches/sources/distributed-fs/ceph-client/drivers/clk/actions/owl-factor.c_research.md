# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-factor.c

Purpose: this file implements OWL factor-table clocks, where a register value maps to arbitrary multiplier/divider pairs rather than a simple linear divider.

Important functions: `_get_table_maxval()`, `_get_table_div_mul()`, and `_get_table_val()` search sentinel-terminated `clk_factor_table` arrays. `owl_clk_val_best()` chooses the best table value for a target rate and optionally asks the parent to round to a better rate when `CLK_SET_RATE_PARENT` is set. `owl_factor_helper_round_rate()` returns the selected rate. `owl_factor_helper_recalc_rate()` reads the hardware value, maps it to `mul/div`, warns on zero divisor unless allowed, and calculates the output. `owl_factor_helper_set_rate()` programs the selected table value into the bitfield.

Control flow/state: calculations are table-driven and state is persisted only in the regmap bitfield. Parent-rate negotiation is done through `clk_hw_round_rate(clk_hw_get_parent(hw), ...)`.

Risks and tests: `_get_table_val()` assumes tables are sorted from faster to slower acceptable rates because it picks the first calculated rate less than or equal to the request. `owl_clk_val_best()` calls `_get_table_maxval(clkt)` after iterating `clkt` to the sentinel when no best value was found, which means it will see only the sentinel rather than the original table; that path deserves focused review. Test signals include factor table ordering, impossible low-rate requests, `CLK_SET_RATE_PARENT` paths, and recalc/set round trips for SD/display/video clocks.
