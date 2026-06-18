# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun9i-a80.h

## Purpose
This private header defines A80 main CCU internal clock IDs that are not fully covered by public dt-bindings and sets the onecell table size.

## Important APIs, Types, And Functions
It includes A80 clock/reset binding headers and defines IDs for CPU PLLs, private PLLs, CPU/bus roots, `CLK_ATS`, `CLK_TRACE`, and `CLK_NUMBER`.

## Control Flow
There is no runtime flow. The constants are consumed by `ccu-sun9i-a80.c` array initializers.

## State And Persistence
No state is stored. Numeric identity is the important contract because DT consumers index the onecell provider by ID.

## Dependencies And Integration Points
Integration is with the main A80 CCU provider and all downstream clock/reset consumers.

## Risks
Changing constants can break ABI or misalign provider arrays. Comments marking exported groups should be preserved to avoid renumbering internal holes.

## Test Signals
Build and A80 DT boot tests should confirm all public binding IDs resolve and no clock lookups return unexpected nulls.
