# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-rtc.h

## Purpose

This header assigns private clock IDs for the RTC CCU helper beyond the public `sun6i-rtc` dt-binding IDs.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun6i-rtc.h` and defines `CLK_IOSC_32K`, `CLK_EXT_OSC32K_GATE`, `CLK_OSC24M_32K`, `CLK_RTC_32K`, and `CLK_NUMBER`.

## Control flow, state, and persistence

There is no executable logic. The constants index the `sun6i_rtc_ccu_hw_clks.hws` onecell slots populated in `ccu-sun6i-rtc.c`.

## Dependencies and integration points

The header is internal to the RTC CCU implementation and extends the public binding namespace without changing DT-visible names directly.

## Risks and test signals

The main risk is ID drift between this header and the onecell initializer. Test by verifying all exported RTC clocks resolve and no consumer receives the wrong hw clock for an ID.
