# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-regmap-mux-div.h

## Purpose
Declares the combined regmap mux/divider descriptor and exported operations.

## Important APIs, Types, And Functions
`struct clk_regmap_mux_div` stores register offset, HID divider field width/shift, source field width/shift, cached divider/source, parent map, embedded `clk_regmap`, optional input PLL pointer, and notifier block. It exports `clk_regmap_mux_div_ops` and `mux_div_set_src_div()`.

## Control Flow
Drivers fill the descriptor, define parent maps as raw hardware source values, and register it with the exported ops. Optional `pclk` and `clk_nb` are available for drivers coordinating parent PLL rate changes.

## State And Persistence
Descriptor fields persist the encoding. Runtime cached `div` and `src` mirror the last successful programming and influence rate-only or parent-only updates.

## Dependencies And Integration Points
Includes CCF and `clk-regmap.h`. It integrates with regmap-backed Qualcomm clock controllers.

## Risks And Edge Cases
The parent map is an array of raw `u32` values rather than `struct parent_map`, so callers must keep parent order and hardware encoding aligned manually.

## Test Signals
Compile coverage and runtime mux/divider rate transitions validate the header.
