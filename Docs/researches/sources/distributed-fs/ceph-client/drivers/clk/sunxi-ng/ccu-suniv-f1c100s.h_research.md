# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-suniv-f1c100s.h

## Purpose
This private header defines internal clock indices for the suniv F1C100s CCU provider and includes public clock/reset bindings.

## Important APIs, Types, And Functions
It maps internal PLL and bus-root IDs such as `CLK_PLL_CPU`, `CLK_PLL_AUDIO_BASE`, `CLK_CPU`, `CLK_AHB`, `CLK_APB`, `CLK_DRAM`, and `CLK_PLL_VIDEO_2X`; exported module and bus IDs come from the dt-binding header.

## Control Flow
There is no runtime flow. The C provider uses the constants to populate `clk_hw_onecell_data`.

## State And Persistence
No mutable state exists. The numeric layout must remain consistent with the provider and binding IDs.

## Dependencies And Integration Points
Integration is with `ccu-suniv-f1c100s.c` and device-tree consumers for the small suniv SoC family.

## Risks
Renumbering can break DT clock specifiers or cause wrong hardware to be controlled. Reserved/exported ranges need to remain aligned with public bindings.

## Test Signals
Build coverage and suniv boot with successful clock lookups validate this header.
