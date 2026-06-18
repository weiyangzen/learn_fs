# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_device.c

## Purpose
This file defines the Poulsbo/GMA500 chipset personality. It wires output initialization, PWM backlight setup, SGX clock-gating initialization, generic display save/restore hooks, register maps, and the `psb_chip_ops` table selected for Poulsbo PCI IDs.

## Important APIs, Types, and Functions
The exported object is `psb_chip_ops`. Important functions are `psb_output_init()`, `psb_backlight_setup()`, `psb_init_pm()`, `psb_save_display_registers()`, `psb_restore_display_registers()`, `psb_power_down()`, `psb_power_up()`, `psb_chip_setup()`, and `psb_chip_teardown()`. `psb_regmap` maps abstract pipe offsets to Poulsbo registers.

## Control Flow
Chip setup selects the register map, discovers core frequency, initializes GMBUS, initializes OpRegion, and parses Intel BIOS data. Output init creates LVDS and SDVO outputs. Backlight setup derives the PWM register period from VBT backlight frequency and core clock, validates bounds, writes `BLC_PWM_CTL`, and sets full brightness. Save/restore locks modeset state, saves shared watermark registers, then delegates CRTC and connector save/restore callbacks.

## State and Persistence Behavior
Persistent state includes `dev_priv->regmap`, VBT-derived `lvds_bl`, saved watermark registers, connector/CRTC save areas, and `BLC_PWM_CTL`. Poulsbo power-up/down hooks are no-ops, unlike Oaktrail display-island gating.

## Dependencies and Integration Points
It integrates with `psb_drv.c` through `psb_ops`, with `psb_intel_display.c` for CRTC helpers, with `psb_intel_lvds.c` for LVDS/backlight, with SDVO output init, GMBUS, OpRegion, and Intel BIOS parsing.

## Risks
Backlight setup depends on valid VBT backlight data; missing or out-of-range values abort setup. Display save/restore assumes connector save callbacks are correctly installed. `psb_chip_teardown()` only tears down GMBUS, while BIOS/OpRegion cleanup is handled elsewhere, so lifecycle ownership is split.

## Test Signals
Signals include Poulsbo PCI IDs selecting `psb_chip_ops`, LVDS/SDVO connectors appearing, PWM backlight initialized from VBT, modes surviving suspend/resume through connector/CRTC save callbacks, and no regressions in SGX clock gating initialization.
