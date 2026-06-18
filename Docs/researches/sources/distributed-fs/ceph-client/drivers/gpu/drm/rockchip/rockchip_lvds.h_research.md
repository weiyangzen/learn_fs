# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_lvds.h

## Purpose

`rockchip_lvds.h` defines register offsets, bit masks, write-mask field helpers, and LVDS format constants for RK3288 and PX30 LVDS hardware.

## Important APIs, Types, and Functions

- RK3288 channel register offsets and lane enable/bias/mode/data bits describe LVDS/TTL lane programming.
- PLL helper macros split feedback and predivider values across RK3288 registers.
- GRF offsets and bits define VOP source selection, LVDS dual-channel, TTL enable, format, start phase, clock inversion, channel enable, and powerdown controls.
- PX30 GRF helpers use `FIELD_PREP_WM16` for write-mask encoded mode, P2S, MSB select, VOP select, clock tie/invert, and format fields.

## Control Flow

The header contains only macros. The C file combines them into poweron, poweroff, and GRF configuration sequences for RK3288 and PX30.

## State and Persistence Behavior

The constants define hardware state programmed by `rockchip_lvds.c`. They do not allocate runtime state. Write-mask macros persist only through GRF register writes.

## Dependencies and Integration Points

The header depends on Linux bit and hardware bitfield helpers. It is private to the Rockchip LVDS driver and tied to SoC register manuals.

## Risks and Edge Cases

Incorrect write-mask field values can overwrite unrelated GRF bits. RK3288 register values such as TX enable are literal hardware values, so changes require validation. The include guard name is nonstandard but functional.

## Test Signals

Register-level tests should compare GRF/MMIO writes for each mapping and output mode. Hardware validation should check lane activity, bit ordering, clock polarity, dual-channel behavior, and PX30 PHY/P2S enablement.
