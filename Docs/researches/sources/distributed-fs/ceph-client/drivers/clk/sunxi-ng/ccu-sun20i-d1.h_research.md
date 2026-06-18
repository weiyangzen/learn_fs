# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun20i-d1.h

## Purpose
`ccu-sun20i-d1.h` is the local header for the D1/R528/T113 main CCU provider. It bridges public clock/reset binding IDs into the C implementation and provides the onecell clock array size.

## Important APIs, Types, And Functions
The header includes `dt-bindings/clock/sun20i-d1-ccu.h` and `dt-bindings/reset/sun20i-d1-ccu.h`. Its only local macro is `CLK_NUMBER`, defined as `CLK_BUS_CAN1 + 1`.

There are no functions or structs.

## Control Flow
No control flow exists. The implementation uses `CLK_NUMBER` to size `sun20i_d1_hw_clks` and uses binding IDs from the included headers to initialize specific slots.

## State And Persistence
The header has compile-time state only: numeric layout and array sizing. It does not store runtime state.

## Dependencies And Integration Points
It must remain synchronized with the public D1 CCU clock and reset bindings and with all initialized IDs in `ccu-sun20i-d1.c`.

## Risks
If the highest valid clock ID changes and `CLK_NUMBER` is not updated, later clock IDs can be truncated from the provider. The macro currently relies on `CLK_BUS_CAN1` being the highest exported ID in the binding, so binding evolution requires careful review.

## Test Signals
Build-time array initializer diagnostics and runtime clock lookup tests are the main signals. Device-tree consumers for high-numbered D1 clocks should resolve successfully, and `clk_summary` should include the expected exported clocks.
