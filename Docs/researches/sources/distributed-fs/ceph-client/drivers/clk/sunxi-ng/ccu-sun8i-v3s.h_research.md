# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-v3s.h

## Purpose
This private header defines internal clock indices for the V3/V3s CCU descriptor and includes public dt-binding IDs for clocks and resets.

## Important APIs, Types, And Functions
It declares non-exported IDs such as `CLK_PLL_CPU`, `CLK_PLL_AUDIO_BASE`, `CLK_AXI`, `CLK_AHB1`, `CLK_APB1`, `CLK_APB2`, `CLK_AHB2`, `CLK_DRAM`, `CLK_MBUS`, and `CLK_PLL_DDR1`. Publicly exported bus and module clock IDs are provided by `dt-bindings/clock/sun8i-v3s-ccu.h`; reset IDs come from the matching reset binding.

## Control Flow
The header has no runtime control flow. It is consumed at compile time by `ccu-sun8i-v3s.c` to size and index `clk_hw_onecell_data` arrays.

## State And Persistence
It stores no state. The numeric constants are ABI-sensitive within the provider tables because device-tree clock specifiers index the same onecell array.

## Dependencies And Integration Points
Dependencies are the dt-binding headers and the C compiler. Integration is direct with the V3/V3s provider and indirect with all DT consumers using exported IDs.

## Risks
Changing numbers can break device-tree ABI or point consumers at the wrong `clk_hw`. Reserved holes document clocks that are not implemented or not exported and should not be compacted casually.

## Test Signals
Build coverage plus DT boot tests are the main signals. Clock-summary names should line up with the binding IDs used by MMC, display, audio, USB, and bus consumers.
