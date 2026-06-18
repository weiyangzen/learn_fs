# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_lvds.c

## Purpose
This file implements the generic Poulsbo LVDS connector and encoder path. It handles LVDS panel/backlight power, I2C or PWM brightness, panel save/restore, mode validation/fixup, panel fitter setup, mode discovery through DDC/VBT/current hardware, connector properties, and LVDS object creation/destruction.

## Important APIs, Types, and Functions
Exported functions/objects are `psb_intel_lvds_set_brightness()`, `psb_intel_lvds_mode_valid()`, `psb_intel_lvds_mode_fixup()`, `psb_intel_lvds_destroy()`, `psb_intel_lvds_set_property()`, `psb_intel_lvds_connector_helper_funcs`, `psb_intel_lvds_connector_funcs`, and `psb_intel_lvds_init()`. Local `struct psb_intel_lvds_priv` stores saved LVDS/panel/backlight registers and an I2C bus.

## Control Flow
Initialization allocates encoder/connector/private state, creates DDC and backlight I2C GPIO buses, initializes connector/encoder, attaches scaling/backlight properties, reads EDID preferred mode, falls back to VBT fixed mode, then falls back to the current hardware-programmed LVDS mode. Mode fixup enforces pipe restrictions, rejects sharing a pipe with another encoder, and replaces adjusted timings with the fixed panel mode. Prepare powers the panel off after saving brightness; commit restores power and brightness. Property changes may trigger a full mode set or backlight update.

## State and Persistence Behavior
Persistent state includes panel fixed mode, backlight duty cycle, LVDS I2C bus, connector save/restore callbacks, saved LVDS registers, and VBT backlight data. Power sequencing writes `PP_CONTROL`, waits on `PP_STATUS`, and caches backlight register state when hardware is off.

## Dependencies and Integration Points
It depends on `gma_i2c_create()`, DDC helper `psb_intel_ddc_get_modes()`, DRM connector helpers, backlight infrastructure via `gma_backlight_set()`, panel/VBT data from BIOS parsing, and CRTC mode readback from `psb_intel_display.c`.

## Risks
`psb_intel_lvds_get_max_backlight()` logs `REG_READ()` even in the powered-off path, which can be unsafe if the register is inaccessible. PWM brightness uses `BUG_ON(max_pwm_blc == 0)`. I2C brightness requires valid VBT `lvds_bl` and target address assumptions. Mode/property setters return `-1` rather than standard errno values. Error paths must free two I2C buses plus DRM objects.

## Test Signals
Signals include LVDS connector creation, EDID/VBT/current-mode fallback selection, pipe restriction enforcement, scaling/backlight properties working through KMS, correct PWM and I2C brightness behavior, panel power sequencing on DPMS, and clean teardown without I2C adapter leaks.
