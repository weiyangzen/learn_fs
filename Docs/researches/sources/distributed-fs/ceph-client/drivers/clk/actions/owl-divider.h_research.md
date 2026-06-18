# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-divider.h

Purpose: this header declares OWL divider clock data structures, instantiation macros, and helper prototypes.

Important types/macros: `struct owl_divider_hw` stores register offset, shift, width, divider flags, and optional `clk_div_table`. `struct owl_divider` embeds that hardware descriptor plus `owl_clk_common`. `OWL_DIVIDER_HW` is the reusable field descriptor used by composites; `OWL_DIVIDER` creates a standalone clock with `owl_divider_ops`.

Control flow/state: runtime callbacks use `hw_to_owl_divider()` to retrieve the descriptor and common regmap. The only durable state is the hardware bitfield described by the macro arguments.

Dependencies and integration: the header depends on `owl-common.h` and exposes helper APIs consumed by `owl-composite.c`. SoC descriptors use `OWL_DIVIDER_HW` inside composite declarations and `OWL_DIVIDER` for bus clocks.

Risks and tests: `width` is used in shifts and masks, so invalid widths can overflow or clear wrong bits. Table pointers must outlive the clock objects; in this driver they are static. Test signals are compile-time macro use, divider table sentinel correctness, and `clk_set_rate()` results observed through `clk_summary`.
