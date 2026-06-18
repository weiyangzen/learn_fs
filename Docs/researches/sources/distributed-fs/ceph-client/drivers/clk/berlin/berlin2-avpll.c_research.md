# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-avpll.c

## Purpose
Implements Berlin2 audio/video PLL VCO and channel clock providers. It models each AVPLL as a VCO plus eight channel clocks, handling production SoC bit-shift and channel-scramble quirks while calculating channel rates from sync and divider registers.

## Important APIs, Types, And Functions
Private types are `berlin2_avpll_vco` and `berlin2_avpll_channel`. Exported registration functions are `berlin2_avpll_vco_register` and `berlin2_avpll_channel_register`. Clock operations include VCO enable/disable/is_enabled/recalc and channel enable/disable/is_enabled/recalc. Quirk handling uses `BERLIN2_AVPLL_BIT_QUIRK`, `BERLIN2_AVPLL_SCRAMBLE_QUIRK`, and `quirk_index`.

## Control Flow
SoC setup registers a VCO clock parented by the reference clock, then registers channel clocks parented by that VCO. VCO recalc reads `VCO_CTRL1` refdiv/fbdiv. Channel recalc checks whether the channel DPLL divider is enabled, reads sync1/sync2, applies optional HDMI, AV1, AV2, and AV3 divisors, accounts for fractional AV2/AV3 behavior, and divides the parent-derived frequency.

## State And Persistence
Each registered clock stores a base address, flags, and channel index. Actual power, sync, divider, and DPLL state resides in AVPLL MMIO registers. Allocation is permanent after early boot registration and has no explicit unregister path in this file.

## Dependencies And Integration Points
Used by `bg2.c` for AVPLL A/B registration. Depends on common clock framework, MMIO accessors, and constants declared in `berlin2-avpll.h`.

## Risks And Edge Cases
Channel 8 is special and lacks normal dividers. BG2/BG2CD quirks shift some fields and scramble channel indexes. Zero sync/divider values can produce invalid or misleading rates if hardware is not initialized. Registration leaks allocations if `clk_hw_register` fails after allocation.

## Test Signals
Validate VCO rates from known refdiv/fbdiv values, channel rates for enabled and bypassed DPLL paths, quirked AVPLL_B channel 1 sync shift, scrambled channel mappings, and enable bits for channels 1 through 7 with channel 8 always enabled.
