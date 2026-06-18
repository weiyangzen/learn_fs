# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-avpll.h

## Purpose
Declares the Berlin2 AVPLL helper interface and quirk flags used by SoC provider files.

## Important APIs, Types, And Functions
Defines `BERLIN2_AVPLL_BIT_QUIRK` for shifted register fields and `BERLIN2_AVPLL_SCRAMBLE_QUIRK` for channel index translation. Declares `berlin2_avpll_vco_register` and `berlin2_avpll_channel_register`.

## Control Flow
No runtime logic exists here. SoC setup code passes MMIO base, names, parent names, indexes, quirk flags, and CCF flags to the implementation in `berlin2-avpll.c`.

## State And Persistence
The header holds only constants and prototypes. Registered clock state is allocated by the implementation.

## Dependencies And Integration Points
Consumed by `bg2.c` and implemented by `berlin2-avpll.c`. It assumes inclusion context provides `BIT`, `u8`, and `void __iomem` definitions through kernel headers.

## Risks And Edge Cases
Incorrect quirk flag choice changes register interpretation for all AVPLL channels. Since the prototypes are `__init` implementations, callers should only use them during early clock setup.

## Test Signals
Compile/link coverage and BG2/BG2CD setup using both quirk flags are the primary signals.
