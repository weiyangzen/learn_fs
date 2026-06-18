# sources/distributed-fs/ceph-client/drivers/clk/sprd/mux.h

## Purpose
Defines Spreadtrum mux clock structures, initialization macros, and helper prototypes.

## Important APIs, Types, And Functions
`struct sprd_mux_ssel` describes source-select shift, width, and optional hardware encoding table. `struct sprd_mux` combines that metadata with `sprd_clk_common`. Macros include `SPRD_MUX_CLK`, `SPRD_MUX_CLK_TABLE`, `SPRD_MUX_CLK_DATA`, and table/data variants. `hw_to_sprd_mux` performs container conversion.

## Control Flow
No direct control flow. Macro expansion binds static mux objects to `sprd_mux_ops`; callbacks in `mux.c` perform register reads and writes.

## State And Persistence
Stores static parent selection metadata and common register information. Parent choice persists in the hardware field.

## Dependencies And Integration Points
Includes `common.h`; included by `composite.h` and SoC files. Parent data variants support modern DT parent descriptions.

## Risks And Edge Cases
Sparse table values must match hardware encodings and parent order. Width/shift mistakes can corrupt adjacent fields. Parent-name versus parent-data macro mismatches can break clock resolution.

## Test Signals
Build coverage for macro variants and runtime parent-resolution tests using `clk_summary` and DT consumers.
