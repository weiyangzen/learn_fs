# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-de2.h

## Purpose

This header defines private intermediate-divider IDs and variant-specific clock counts for the DE2 CCU driver.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-de2.h` and `dt-bindings/reset/sun8i-de2.h`, defines `CLK_MIXER0_DIV`, `CLK_MIXER1_DIV`, `CLK_WB_DIV`, `CLK_ROT_DIV`, `CLK_NUMBER_WITH_ROT`, and `CLK_NUMBER_WITHOUT_ROT`.

## Control flow, state, and persistence

There is no runtime behavior. The IDs let the driver expose module gates and also keep intermediate dividers in the onecell data.

## Dependencies and integration points

The header is internal to `ccu-sun8i-de2.c`; public display-engine consumers use the dt-binding IDs while the driver uses the private divider slots for parent relationships.

## Risks and test signals

Variant counts must match whether rotation exists. A wrong count can hide valid clocks or expose uninitialized slots. Test by resolving clocks for one-mixer, two-mixer, and rotation-capable display engines.
