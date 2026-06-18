# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-h3.h

## Purpose

This private header defines the H3/H5 CCU internal clock IDs and variant-specific onecell sizes.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-h3-ccu.h` and `dt-bindings/reset/sun8i-h3-ccu.h`, defines internal PLL/audio/bus IDs, and provides `CLK_NUMBER_H3` and `CLK_NUMBER_H5`.

## Control flow, state, and persistence

There is no executable code. The constants index the H3 and H5 onecell arrays in `ccu-sun8i-h3.c`.

## Dependencies and integration points

The header must stay aligned with both public binding IDs and the two descriptor variants. Comments indicate which clock families are exported by binding ranges.

## Risks and test signals

The main risk is H3/H5 count or ID mismatch, especially for H5-only `CLK_BUS_SCR1`. Test by resolving all H3 and H5 binding clocks and checking no out-of-range onecell access occurs.
