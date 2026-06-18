# sources/distributed-fs/ceph-client/drivers/video/backlight/rave-sp-backlight.c

Purpose: backlight driver for Zodiac RAVE SP-controlled LCD backlights. It exposes a platform backlight device and sends a fixed RAVE SP command packet to the parent controller.

Important APIs/types/functions: `rave_sp_backlight_update_status()` is the only runtime operation. It builds a five-byte command beginning with `RAVE_SP_CMD_SET_BACKLIGHT` and places `RAVE_SP_BACKLIGHT_LCD_EN | intensity` in byte 2 when brightness is nonzero and power is `BACKLIGHT_POWER_ON`. Probe registers with `devm_backlight_device_register()` using parent `struct rave_sp` as backlight data.

Control flow: backlight core calls update, update derives intensity from `bd->props.power` and `bd->props.brightness`, then sends it with `rave_sp_exec()`. Probe skips initial `backlight_update_status()` when the DT node has a phandle, assuming another device will coordinate status; otherwise it pushes the default state immediately.

State and persistence: no private state is allocated. Brightness/power live in the backlight core; actual persistence is in the RAVE SP controller firmware.

Dependencies and integration: platform device, OF compatible `zii,rave-sp-backlight`, parent RAVE SP MFD driver, backlight core with suspend/resume option.

Risks: `dev->of_node` is dereferenced unconditionally in probe, so non-OF instantiation would fail. Brightness is a `u8` and max is 100, which matches props but relies on core clamping. Test signals include power-off forcing zero intensity, phandle-controlled deferred initial update, parent command failure propagation, and suspend/resume updates.
