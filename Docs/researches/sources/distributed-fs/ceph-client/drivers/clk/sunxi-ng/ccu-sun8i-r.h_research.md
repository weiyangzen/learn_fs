# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r.h

## Purpose

This header defines internal clock IDs for the sun8i PRCM/R-domain CCU driver.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-r-ccu.h` and `dt-bindings/reset/sun8i-r-ccu.h`, defines private `CLK_AHB0` and `CLK_APB0`, and sets `CLK_NUMBER` to `CLK_IR + 1`.

## Control flow, state, and persistence

There is no runtime code. The IDs are used by the variant onecell arrays in `ccu-sun8i-r.c`.

## Dependencies and integration points

The header extends the public R-domain binding with internal bus-clock slots that are not exported as standalone binding IDs.

## Risks and test signals

Incorrect IDs can miswire AR100/APB0/peripheral gates. Test with `clk_summary` and DT consumers for all R-domain clocks.
