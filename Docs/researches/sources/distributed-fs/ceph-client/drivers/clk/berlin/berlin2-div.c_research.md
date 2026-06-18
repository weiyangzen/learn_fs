# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-div.c

## Purpose
Implements Berlin2 composite divider cells that may include an input PLL mux, programmable divider, divide-by-3 bypass path, and gate. It wraps this hardware in CCF composite clock registration.

## Important APIs, Types, And Functions
Private `struct berlin2_div` stores `clk_hw`, base, copied `berlin2_div_map`, and optional lock. The exported `berlin2_div_register` creates a composite clock. Operations include `berlin2_div_is_enabled`, `berlin2_div_enable`, `berlin2_div_disable`, `berlin2_div_set_parent`, `berlin2_div_get_parent`, and `berlin2_div_recalc_rate`.

## Control Flow
Registration copies the map, chooses mux/rate/gate ops based on flags, and calls `clk_hw_register_composite`. Parent selection toggles `PLL_SWITCH`, then programs `PLL_SELECT` for nonzero parent indexes. Rate recalc checks divide-by-3 switch first, then divider bypass, otherwise maps `DIV_SELECT` through the fixed divider table `{1,2,4,6,8,12,1,1}`.

## State And Persistence
Per-clock software state is the copied map and base pointer. Hardware registers persist selected parent, divider selection, divide-by-3 switch, divider bypass, and gate enable. The optional spinlock serializes shared register updates across Berlin clock cells.

## Dependencies And Integration Points
Used by `bg2.c` and `bg2q.c` with maps from `berlin2-div.h`. Integrates with common clock composite helpers and shared SoC register locks.

## Risks And Edge Cases
Only recalc is implemented for rate; `determine_rate` is no-reparent and there is no divider programming path. Parent indexes assume the hardware encoding where index 0 means bypass and index >0 maps to `PLL_SELECT=index-1`. Missing locks around shared registers would race with mux/gate changes.

## Test Signals
Check parent get/set encodings, divide-by-3 dominance, divider bypass, all divider table values, optional gate/mux flag combinations, and concurrent register access under the shared spinlock.
