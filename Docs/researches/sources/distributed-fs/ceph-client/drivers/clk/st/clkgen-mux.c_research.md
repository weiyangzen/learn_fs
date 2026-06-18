# sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-mux.c

## Purpose
This file registers a small ST clock-generator mux provider, currently for the STiH407 A9 mux compatible.

## Important APIs, Types, And Functions
`struct clkgen_mux_data` describes offset, shift, width, lock, clock flags, and mux flags. `clkgen_mux_get_parents()` reads OF parents into an allocated name array. `st_of_clkgen_mux_setup()` maps registers and calls `clk_register_mux()`. `st_of_clkgen_a9_mux_setup()` supplies `stih407_a9_mux_data` and is bound by `CLK_OF_DECLARE(clkgen_a9mux, "st,stih407-clkgen-a9-mux", ...)`.

## Control Flow
Setup first maps a `reg` property on the mux node. For backward compatibility it falls back to the parent node register resource. It registers a mux clock named after the OF node with `CLK_SET_RATE_PARENT`, then publishes it as a simple OF clock provider.

## State And Persistence
The parent selection persists in the mapped hardware mux register. The provider keeps allocated parent-name storage for the registered clock. Shared A9 access uses `clkgen_a9_lock` from `clkgen-pll.c`.

## Dependencies And Integration Points
It depends on OF clock parents, OF address mapping, `clk_register_mux()`, and `clkgen.h` for the external A9 lock declaration. Consumers obtain the mux clock directly from the node.

## Risks
The fallback parent-node mapping must match legacy DT layout or the mux will access the wrong register base. The clock name is `np->name`, so DT node naming changes can affect debug visibility. Error handling unmaps on setup failure but early-registered clocks are not dynamically removed.

## Test Signals
Boot logs should show provider registration. Debugfs/clk summary should show the mux parent, and CPU/A9 rate-change paths should verify parent switching under the shared lock.
