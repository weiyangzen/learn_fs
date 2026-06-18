# sources/distributed-fs/ceph-client/drivers/clk/sprd/composite.h

## Purpose
Declares the Spreadtrum composite clock structure and macro family used by SoC tables.

## Important APIs, Types, And Functions
`struct sprd_comp` embeds `struct sprd_mux_ssel`, `struct sprd_div_internal`, and `struct sprd_clk_common`. Macros such as `SPRD_COMP_CLK`, `SPRD_COMP_CLK_TABLE`, `SPRD_COMP_CLK_DATA`, and offset variants initialize composite clocks with parent-name arrays or `clk_parent_data`. `hw_to_sprd_comp` recovers the composite from a `clk_hw`.

## Control Flow
The macros create static clock objects with register offset, mux field, divider field, parent descriptors, flags, and `sprd_comp_ops`. Runtime control passes through the ops defined in `composite.c`.

## State And Persistence
Stores mux/divider field metadata and common register state for each static SoC clock. Hardware register values persist outside the structure.

## Dependencies And Integration Points
Includes `common.h`, `mux.h`, and `div.h`. Used heavily by SC9860 and SC9863A SoC files for clocks that need both source selection and divisors.

## Risks And Edge Cases
Macro argument order is dense and easy to misread; swapped shifts, widths, or offsets silently target wrong fields. Parent-data variants must match whether the parent is named by firmware name, direct hw pointer, or legacy string.

## Test Signals
Build coverage catches type mismatches. Hardware validation should confirm generated clock names, parent counts, mux table mappings, and rate changes for each macro instance.
