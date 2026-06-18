# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-divider.c

Purpose: this file implements OWL divider clocks and divider helper routines used by standalone and composite clocks.

Important functions: `owl_divider_determine_rate()` calls the common `divider_determine_rate()` with the table, width, and flags. `owl_divider_helper_recalc_rate()` reads the register, extracts the configured value, and calls `divider_recalc_rate()`. `owl_divider_helper_set_rate()` computes a hardware value with `divider_get_val()`, clears the target bitfield with `GENMASK`, writes the new field, and returns success. `owl_divider_ops` exposes recalc, determine, and set-rate callbacks.

Control flow/state: each callback reads or writes a field in the clock controller regmap. There is no separate cached divider state. The clock framework passes parent rates and requested rates to these callbacks.

Dependencies and risks: depends on common clock divider helpers, `regmap_read`, and `regmap_write`. A notable risk is that `owl_divider_helper_set_rate()` passes `0` rather than `div_hw->div_flags` to `divider_get_val()`, so flags used for determine/recalc may not affect programming. Register read-modify-write is unprotected at this layer. Test signals are rate set/recalc consistency, table-backed divider coverage, and hardware register field validation.
