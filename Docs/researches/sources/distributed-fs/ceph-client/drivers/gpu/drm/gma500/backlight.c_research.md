<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/backlight.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/backlight.c

## Purpose

This file provides the common GMA500 backlight class-device glue. It tracks logical backlight enable/level state and delegates hardware-specific get/set/init behavior through the chip `psb_ops` table.

## Important APIs, Types, And Functions

Exported functions are `gma_backlight_enable()`, `gma_backlight_disable()`, `gma_backlight_set()`, `gma_backlight_init()`, and `gma_backlight_exit()`. Local backlight ops are `gma_backlight_get_brightness()` and `gma_backlight_update_status()`. It uses `dev_priv->ops->backlight_init`, `backlight_get`, `backlight_set`, and `backlight_name`.

## Control Flow

Initialization defaults the driver state to enabled at level 100, calls the chip-specific backlight init, then skips native registration if ACPI video policy says not to use native backlight. With `CONFIG_BACKLIGHT_CLASS_DEVICE`, it registers a raw backlight device with max `PSB_MAX_BRIGHTNESS`. Updates clamp visible brightness to at least 1, store `dev_priv->backlight_level`, and call the hardware setter only if `backlight_enabled` is true. Enable restores the saved level; disable writes hardware level zero.

## State And Persistence

Persistent state is in `drm_psb_private`: `backlight_enabled`, `backlight_level`, and optional `backlight_device`. Hardware PWM or platform backlight registers are owned by chip-specific callbacks such as Cedarview's `cdv_set_brightness()`.

## Dependencies And Integration Points

It depends on Linux backlight and ACPI video policy, DRM logging, `psb_drv.h`, register headers, BIOS definitions, and power helpers. LVDS/eDP paths call the enable/disable/set helpers during panel sequencing.

## Risks And Test Signals

Risks include forcing minimum userspace brightness to 1, divergence between stored level and hardware if chip callbacks fail silently, and no class device when ACPI chooses firmware/vendor backlight. Test signals are ACPI native/non-native policy, class device registration/removal, brightness reads through chip getter, DPMS panel off/on, and suspend/resume backlight restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/backlight.c -->
