# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r40.h

## Purpose

This private header defines the internal clock-index layout for the R40 CCU driver.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-r40-ccu.h` and `dt-bindings/reset/sun8i-r40-ccu.h`, then defines IDs for `CLK_OSC_12M`, PLL CPU/audio/video/VE/DDR/peripheral/SATA/GPU/MIPI/DE clocks, bus clocks, `CLK_DRAM`, and `CLK_NUMBER`.

## Control flow, state, and persistence

There is no executable behavior. The constants map directly to slots in `sun8i_r40_hw_clks`.

## Dependencies and integration points

The header connects public binding IDs to private internal slots used by the R40 CCU source. Comments mark large exported ranges for bus/module/DRAM clocks.

## Risks and test signals

Index mistakes are high impact because the R40 onecell table is large. `CLK_NUMBER` must track `CLK_OUTB + 1`, and all skipped public-exported IDs must remain intentionally handled by the binding. Test by resolving all R40 binding clocks and checking no consumer receives a mismatched parent or rate.
