# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100-r.h

## Purpose
`ccu-sun50i-a100-r.h` is the local header for the A100 PRCM CCU provider. It imports public binding IDs and defines internal/local clock index constants used by `ccu-sun50i-a100-r.c`.

## Important APIs, Types, And Functions
The header includes `dt-bindings/clock/sun50i-a100-r-ccu.h` and `dt-bindings/reset/sun50i-a100-r-ccu.h`. It defines `CLK_R_CPUS`, `CLK_R_AHB`, and `CLK_R_APB2`, notes that APB1 is exported for R_PIO but not locally assigned in the same way, and defines `CLK_NUMBER` as `CLK_R_AHB_BUS_RTC + 1`.

There are no functions or structs.

## Control Flow
No local control flow exists. The constants size and index the onecell clock array in the C provider.

## State And Persistence
No runtime state is present. The header provides compile-time ID layout.

## Dependencies And Integration Points
It must remain synchronized with the public A100 R CCU binding and the provider's `sun50i_a100_r_hw_clks` initializer.

## Risks
The comment about APB1 being exported for R_PIO indicates a deliberate ID-layout gap. Collapsing or renumbering these constants would break device-tree clock lookups. `CLK_NUMBER` must track the highest exported binding ID.

## Test Signals
Builds should have no initializer bounds warnings. Runtime tests should confirm all exported R-CCU clocks resolve by their binding IDs, especially around the APB1/APB2 ID gap.
