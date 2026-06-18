# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-a10-hosc.c

## Purpose
This legacy provider registers the gated 24 MHz high-speed oscillator as a composite fixed-rate plus gate clock.

## Important APIs, Types, And Functions
The setup function `sun4i_osc_clk_setup()` handles `allwinner,sun4i-a10-osc-clk`. It allocates `clk_fixed_rate` and `clk_gate`, reads `clock-frequency`, maps the gate register, and registers a composite clock.

## Control Flow
Early OF init reads the frequency, allocates components, fills gate bit 0 and fixed-rate data, registers the composite, and adds a simple provider.

## State And Persistence
State is the oscillator gate bit and registered CCF objects. The frequency comes from DT; there is no runtime recalculation beyond fixed-rate ops.

## Dependencies And Integration Points
It depends on CCF, OF properties, OF mapping, and dynamic allocation. It is a root parent for many legacy sunxi clocks.

## Risks
Failure to map the register after allocation can leak resources, consistent with early boot provider style. Wrong frequency in DT propagates to every child clock.

## Test Signals
Test by checking root oscillator rate in clk-summary and successful boot of downstream legacy clocks.
