# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80-de.h

## Purpose
This private header sizes the A80 Display Engine CCU onecell clock table and reserves IDs for internal FE/BE divider clocks.

## Important APIs, Types, And Functions
It includes `dt-bindings/clock/sun9i-a80-de.h` and `dt-bindings/reset/sun9i-a80-de.h`, then defines `CLK_FE0_DIV` through `CLK_BE2_DIV` and `CLK_NUMBER`.

## Control Flow
There is no runtime flow; the C provider uses these constants for array initializers and provider size.

## State And Persistence
No mutable state is present. The constants are compile-time table indexes and must remain aligned with `ccu-sun9i-a80-de.c`.

## Dependencies And Integration Points
It integrates with the DE clock provider and the public binding IDs consumed by the display subsystem.

## Risks
Risk is low but ABI-adjacent: adding internal clocks below public IDs or changing `CLK_NUMBER` incorrectly can make onecell lookups fail or expose null clocks.

## Test Signals
Build and probe coverage are sufficient, with clk-summary confirming divider clocks exist only as provider internals used by FE/BE gates.
