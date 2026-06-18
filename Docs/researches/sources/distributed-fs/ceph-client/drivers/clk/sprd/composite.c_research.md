# sources/distributed-fs/ceph-client/drivers/clk/sprd/composite.c

## Purpose
Implements Spreadtrum composite clocks that combine parent selection and divider control in one clock hardware object.

## Important APIs, Types, And Functions
Exports `sprd_comp_ops`. Internal callbacks are `sprd_comp_get_parent`, `sprd_comp_set_parent`, `sprd_comp_determine_rate`, `sprd_comp_recalc_rate`, and `sprd_comp_set_rate`. They delegate to mux helpers from `mux.c` and divider helpers from `div.c`.

## Control Flow
CCF calls the composite ops. Parent operations read or write the mux field in the shared register. Rate operations determine divider feasibility, recalculate from the divider field, or write a new divider while preserving unrelated bits.

## State And Persistence
No private state beyond `struct sprd_comp`; parent and rate state persist in regmap-backed hardware registers.

## Dependencies And Integration Points
Depends on `struct sprd_comp` from `composite.h`, `sprd_mux_helper_*`, `sprd_div_helper_*`, and CCF divider algorithms. SoC files instantiate these clocks for UART, I2C, SPI, buses, CPU, GPU, display, and sensor domains.

## Risks And Edge Cases
Mux and divider updates are separate read-modify-write operations without an explicit lock in this layer, so concurrent updates to the same register fields rely on regmap serialization and non-overlapping fields. `determine_rate` only considers divider width and does not select a better parent itself.

## Test Signals
Clock summary should report correct parent and divided rates. Runtime tests include changing rates on composite peripheral clocks and checking that parent selection and divider fields both reflect the requested configuration.
