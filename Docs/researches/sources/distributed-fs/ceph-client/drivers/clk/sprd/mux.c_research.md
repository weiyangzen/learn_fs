# sources/distributed-fs/ceph-client/drivers/clk/sprd/mux.c

## Purpose
Implements Spreadtrum mux-only clocks and helper routines reused by composite clocks.

## Important APIs, Types, And Functions
Exports `sprd_mux_ops`, `sprd_mux_helper_get_parent`, and `sprd_mux_helper_set_parent`. `sprd_mux_ops` provides get/set parent plus `__clk_mux_determine_rate`.

## Control Flow
Get-parent reads the mux field from the register. Without a table it returns the raw encoded value; with a table it maps sparse or ranged hardware encodings back to CCF parent indexes. Set-parent optionally maps the CCF index through the table, clears the mux field, and writes the encoded value.

## State And Persistence
Parent selection persists in hardware registers. In-memory state is limited to mux shift, width, optional table, and common register metadata.

## Dependencies And Integration Points
Depends on CCF parent APIs, regmap, and `mux.h`. Composite clocks call the helper functions; SoC files instantiate standalone muxes for bus, reference, and peripheral selectors.

## Risks And Edge Cases
Table mapping assumes monotonic table values and treats the last parent as a fallback. Read/write errors are ignored. Read-modify-write is not locally locked, so fields sharing a register require care.

## Test Signals
Parent switching should update expected register bits and clock summary parent names. Sparse-table muxes such as MCU selectors need explicit tests for each encoded parent.
