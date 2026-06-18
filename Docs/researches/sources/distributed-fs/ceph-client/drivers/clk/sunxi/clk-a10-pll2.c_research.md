# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-pll2.c

## Purpose
This legacy provider registers the A10/A13 PLL2 audio clock and its four fixed-factor outputs.

## Important APIs, Types, And Functions
Important logic is `sun4i_pll2_setup()`, wrappers for A10 and A13 compatibles, divider/multiplier/gate composite setup for `pll2-base`, and fixed-factor outputs indexed by `dt-bindings/clock/sun4i-a10-pll2.h`.

## Control Flow
Early init maps MMIO, allocates a onecell provider, registers a predivider, gate, multiplier composite, forces the post divider register field to 4 with an SoC-specific offset, registers 1x/2x/4x/8x outputs, and adds the onecell provider.

## State And Persistence
State is PLL2 register fields and registered CCF clocks. Probe writes the postdivider value during initialization.

## Dependencies And Integration Points
It depends on CCF divider/multiplier/gate/fixed-factor helpers, OF mapping, allocations, and PLL2 binding IDs. It integrates with legacy audio clock consumers.

## Risks
PLL2 is audio-critical; postdivider offset differs between A10 and A13. Partial registration failures can leave earlier clocks registered. Incorrect fixed factors break audio sample-rate families.

## Test Signals
Test by booting A10/A13 DTs, inspecting PLL2 output rates, and validating audio playback at 44.1/48 kHz families.
