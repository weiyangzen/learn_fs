# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-div.h

## Purpose
Defines Berlin2 divider-cell descriptor structures and macros for mapping logical mux/divider/gate controls onto scattered SoC registers.

## Important APIs, Types, And Functions
Flags `BERLIN2_DIV_HAS_GATE` and `BERLIN2_DIV_HAS_MUX` select composite sub-ops. Mapping macros include `BERLIN2_PLL_SELECT`, `BERLIN2_PLL_SWITCH`, `BERLIN2_DIV_SELECT`, `BERLIN2_DIV_SWITCH`, `BERLIN2_DIV_D3SWITCH`, `BERLIN2_DIV_GATE`, and `BERLIN2_SINGLE_DIV`. Structures are `berlin2_div_map` and `berlin2_div_data`. The exported constructor is `berlin2_div_register`.

## Control Flow
No code executes in the header. SoC files populate `berlin2_div_data` arrays; `berlin2_div_register` consumes each map to register a composite CCF clock.

## State And Persistence
Maps are typically `__initconst`; the implementation copies them into permanent per-clock state so early init data can be discarded.

## Dependencies And Integration Points
Consumed by Berlin SoC provider files and implemented by `berlin2-div.c`. Parent IDs in `berlin2_div_data` are translated by SoC files into parent name arrays.

## Risks And Edge Cases
The macros only describe offsets and shifts; they do not validate that fields fit in registers or do not overlap. Shared-register maps must use the same lock at registration.

## Test Signals
Build coverage for single-register and scattered-register maps, gate-less and mux-less cells, and parent-name generation from `parent_ids` arrays.
