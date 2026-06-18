# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a100.h

## Purpose
`ccu-sun50i-a100.h` is the local header for the A100 main CCU provider. It imports public clock/reset IDs and defines internal clock indices and array sizing used by `ccu-sun50i-a100.c`.

## Important APIs, Types, And Functions
The header includes `dt-bindings/clock/sun50i-a100-ccu.h` and `dt-bindings/reset/sun50i-a100-ccu.h`. It defines internal indices for `CLK_OSC12M`, PLLs, PLL postdiv/fixed-factor outputs, CPU/fabric clocks, AXI, CPUX APB, PSI/AHB, AHB3, APB2, and `CLK_BUS_DRAM`, while comments document exported binding holes such as `PLL_PERIPH0`, `CPUX`, APB1 for PIO, and all non-DRAM module clocks.

`CLK_NUMBER` is defined as `CLK_CSI_ISP + 1`, sizing the public onecell clock array.

## Control Flow
There is no control flow. The C provider uses the constants for onecell array indexing and to distinguish internal helper clocks from public binding IDs.

## State And Persistence
The header stores no runtime state. It defines compile-time layout for clock IDs.

## Dependencies And Integration Points
It must remain synchronized with the A100 public clock/reset binding headers and the provider's `sun50i_a100_hw_clks` array. It is the local coordination point between binding-visible IDs and internal helper clocks such as PLL factor/postdivider outputs.

## Risks
The file intentionally leaves holes and comments for clocks exported by bindings or special consumers. Renumbering these local definitions would break device-tree ABI expectations. `CLK_NUMBER` must track the highest exported ID; otherwise high-numbered media clocks can be silently unavailable.

## Test Signals
Build signals include no array initializer overflow warnings. Runtime signals include successful lookup of all A100 public clock IDs, especially high-numbered media and CSI/ISP clocks, and expected omission or internal-only behavior for commented helper clocks.
