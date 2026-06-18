# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-factor.h

Purpose: this header defines the OWL factor clock model and helper API.

Important types/macros: `struct clk_factor_table` maps a register `val` to `mul` and `div`. `struct owl_factor_hw` stores register location, bitfield width/shift, flags, and the table. `struct owl_factor` combines the descriptor with `owl_clk_common`. `OWL_FACTOR_HW` creates a reusable descriptor and `OWL_FACTOR` creates a standalone factor clock. `div_mask(d)` derives the maximum encodable value from width.

Control flow/state: factor clocks use the table to translate between framework rates and hardware values. State is persisted in the register field; software state is static descriptor data.

Dependencies and integration: used directly by `owl-factor.c`, by composite clocks, and by SoC files for SD, display, video, GPU, and bus factors.

Risks and tests: table sentinel entries must have `div == 0`. The `div_mask` macro uses `1 << width`, so width must be valid for the integer type. The declared `fct_flags` are only used for zero-divisor warning behavior. Test signals are sentinel validation, mask boundary coverage, and comparing hardware register values against expected `mul/div` tables.
