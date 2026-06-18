# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_lvds.c

## Purpose
This file implements the Oaktrail LVDS connector/encoder path. It powers the panel, programs LVDS and panel-fitter registers, discovers a fixed panel mode from EDID/GCT/VBT, attaches scaling and backlight properties, and wires Oaktrail-specific encoder helpers.

## Important APIs, Types, and Functions
The exported API is `oaktrail_lvds_init()`. Important helpers are `oaktrail_lvds_set_power()`, `oaktrail_lvds_dpms()`, `oaktrail_lvds_mode_set()`, `oaktrail_lvds_prepare()`, `oaktrail_lvds_commit()`, `oaktrail_lvds_get_max_backlight()`, and `oaktrail_lvds_get_configuration_mode()`. It reuses connector funcs from `psb_intel_lvds.c` and mode fixup from `psb_intel_lvds_mode_fixup()`.

## Control Flow
Initialization allocates encoder and connector objects, initializes a LVDS connector and encoder, attaches scaling/backlight properties, derives dither preference from GCT or driver flags, then probes EDID. It first tries the chip ops I2C bus, then an LPC GPIO bit-banged bus if available, assigns `connector->ddc`, and stores a preferred mode from EDID. If EDID is unavailable, it builds a mode from GCT timing, then VBT fallback modes. Prepare saves backlight PWM and powers the panel down; commit restores power and brightness.

## State and Persistence Behavior
Persistent state is in `mode_dev->panel_fixed_mode`, `mode_dev->panel_wants_dither`, `mode_dev->backlight_duty_cycle`, connector DDC pointer, and `dev_priv->is_lvds_on`. Panel power changes update `PP_CONTROL`, wait on `PP_STATUS`, and optionally call a chip-specific LVDS backlight power hook.

## Dependencies and Integration Points
It depends on MID GCT data from `mid_bios.c`, generic LVDS connector funcs in `psb_intel_lvds.c`, LPC I2C from `oaktrail_lvds_i2c.c`, GMA power helpers, DRM EDID helpers, and mode properties from DRM core.

## Risks
If EDID is unavailable and GCT/VBT data is bad, the panel mode will be wrong. The code sets `connector->ddc` manually after probing because the adapter may be discovered late. Error paths must release the optional LPC DDC bus or I2C adapter correctly. Power loops wait indefinitely on panel status bits.

## Test Signals
Signals include LVDS connector registration only when fused for LVDS, preferred mode from EDID or GCT, correct scaling property behavior, dither bit programming when requested, backlight/panel power toggles on DPMS, and no leaks in failed probe paths.
