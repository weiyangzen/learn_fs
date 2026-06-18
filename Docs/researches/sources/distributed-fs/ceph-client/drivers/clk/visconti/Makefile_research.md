<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/visconti/Makefile

## Purpose

The Visconti Makefile builds common and TMPV770x-specific clock-controller support.

## Important APIs, Types, And Functions

`clkc.o`, `pll.o`, and `reset.o` are common helpers. `pll-tmpv770x.o` and `clkc-tmpv770x.o` provide SoC-specific PLL and PISMU clock/reset tables.

## Control Flow

All objects are linked with `obj-y` when the directory is selected. PLL setup uses early OF declaration; clock/reset setup uses a built-in platform driver.

## State And Persistence Behavior

No state is stored here. Object inclusion determines which providers are present.

## Dependencies And Integration Points

It integrates the Visconti common clock, PLL, and reset helper split with Kbuild.

## Risks And Test Signals

Separating common and SoC files would break helper references. Build the Visconti config and verify both PLL and PISMU compatible strings probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/visconti/Makefile -->
