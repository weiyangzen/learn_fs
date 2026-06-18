# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun4i-a10.h

## Purpose
`ccu-sun4i-a10.h` is the local header for the shared A10/A20 CCU provider. It imports public clock/reset binding IDs and defines internal clock indices plus the total clock counts for the two supported SoCs.

## Important APIs, Types, And Functions
The header includes `dt-bindings/clock/sun4i-a10-ccu.h`, `dt-bindings/clock/sun7i-a20-ccu.h`, and `dt-bindings/reset/sun4i-a10-ccu.h`. It defines internal indexes for PLLs, CPU/AXI/AHB/APB clocks, and comments which public ranges are exported for AHB, APB, IP module, DRAM, and media clocks. `CLK_NUMBER_SUN4I` is `CLK_MBUS + 1`; `CLK_NUMBER_SUN7I` is `CLK_OUT_B + 1`.

There are no functions or C structs.

## Control Flow
No control flow is present. The C file uses these constants to size and populate separate `clk_hw_onecell_data` arrays for A10 and A20.

## State And Persistence
This header has no runtime state. Its compile-time numeric constants define clock lookup table layout.

## Dependencies And Integration Points
It is the local bridge between two public binding namespaces and the shared implementation. It must stay synchronized with both A10 and A20 binding headers and the provider's SoC-specific onecell arrays.

## Risks
The dual-SoC nature is the main risk. A clock index valid on A20 may not be valid on A10, and the two `CLK_NUMBER_*` limits differ. A bad size macro can truncate A20-only clocks or expose unimplemented A10 clocks.

## Test Signals
Builds should show no initializer bounds warnings. Runtime clock lookup should work for common A10/A20 clocks and for A20-only outputs such as the higher `CLK_OUT_B` range, while unimplemented clocks such as the noted GPS clock remain handled as expected.
