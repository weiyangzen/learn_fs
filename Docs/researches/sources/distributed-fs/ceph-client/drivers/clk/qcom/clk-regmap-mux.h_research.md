# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux.h

## Purpose
Declares the simple regmap mux descriptor used by `clk-regmap-mux.c`.

## Important APIs, Types, And Functions
`struct clk_regmap_mux` stores register, shift, width, optional `struct parent_map`, and embedded `clk_regmap`. The header exports `clk_regmap_mux_closest_ops`.

## Control Flow
Drivers instantiate the descriptor and register it with the exported ops. Runtime parent read/write behavior is implemented in the C file.

## State And Persistence
The descriptor maps CCF parent indices to hardware source fields. Hardware persists the selected source.

## Dependencies And Integration Points
Includes CCF, `clk-regmap.h`, and qcom `common.h`. It integrates with SoC clock tables that use `struct parent_map`.

## Risks And Edge Cases
The descriptor has no explicit lock, so serialization relies on regmap and higher-level clock framework locking.

## Test Signals
Build coverage and parent switching through CCF validate the header.
