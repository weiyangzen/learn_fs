# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds_regs.h

## Purpose

`rcar_lvds_regs.h` defines register offsets and bitfields for the R-Car LVDS encoder and its Gen2, Gen3, D3, and E3 PLL variants.

## Important APIs, Types, and Functions

The macro API covers `LVDCR0`, `LVDCR1`, `LVDPLLCR`, `LVDCTRCR`, `LVDCHCR`, `LVDSTRIPE`, `LVDSCR`, and `LVDDIV`. Fields encode LVDS mode, power/reset/enable ordering, channel standby/routing, simple PLL delays/dividers, extended PLL source and multiplier/divider settings, control-signal muxing, dual-link striping, and output divider control.

## Control Flow

`rcar_lvds.c` uses these definitions to build register values during enable, disable, PLL setup, lane routing, and dual-link striping. The macros encode generation-specific fields that must be selected by SoC quirk data.

## State and Persistence Behavior

The header owns no software state. It describes persistent hardware register state written by the LVDS driver.

## Dependencies and Integration Points

It integrates only with the R-Car LVDS bridge implementation and hardware documentation. No external Linux APIs are required beyond the preprocessor.

## Risks and Edge Cases

- Many bits have different meanings between Gen2 and Gen3 (`BEN` vs `PWD`, simple vs extended PLL fields).
- Extended PLL field macros do not mask inputs, so callers must validate ranges.
- Incorrect channel or stripe settings can produce swapped lanes or wrong dual-link pixel order.

## Test Signals

Register trace comparison against expected LVDS enable/disable sequences on Gen2, Gen3, D3, and E3 platforms is the main validation signal.
