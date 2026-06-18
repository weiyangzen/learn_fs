# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1-r.h

## Purpose
`ccu-sun20i-d1-r.h` is the local private header for the D1/R528/T113 PRCM CCU provider. It imports the public device-tree clock/reset IDs and defines internal clock indices needed by `ccu-sun20i-d1-r.c`.

## Important APIs, Types, And Functions
There are no functions or types. The header includes `dt-bindings/clock/sun20i-d1-r-ccu.h` and `dt-bindings/reset/sun20i-d1-r-ccu.h`, defines the internal `CLK_R_APB0` index as `1`, and defines `CLK_NUMBER` as `CLK_BUS_R_CPUCFG + 1` for sizing the onecell hardware clock array.

## Control Flow
No control flow is present. The C file uses these constants to place clock hardware pointers at the IDs expected by device-tree consumers.

## State And Persistence
The header contains no state. Its constants determine array sizing and clock ID layout at compile time.

## Dependencies And Integration Points
It integrates the local C provider with the public clock and reset binding headers. `CLK_NUMBER` must remain in sync with the highest exported binding ID used by the provider.

## Risks
If `CLK_NUMBER` is too small or an internal index collides with a binding ID, CCF registration may omit a clock or expose the wrong hardware pointer for a device-tree ID. Because the file is tiny, the main maintenance risk is forgetting to update it when binding IDs change.

## Test Signals
Builds should complete without array initializer warnings. Runtime tests should confirm every exported D1 R-CCU clock ID resolves and that no valid device-tree clock index returns `NULL` unexpectedly.
