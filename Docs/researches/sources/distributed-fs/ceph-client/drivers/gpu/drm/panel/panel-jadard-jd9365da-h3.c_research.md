# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jadard-jd9365da-h3.c

## Purpose

This DRM MIPI DSI panel driver supports several panels using the Jadard JD9365DA-H3 controller family. Each compatible supplies fixed mode data, DSI settings, an init callback, and optional LP11/reset/powerdown timing quirks.

## Important APIs, Types, And Functions

- `struct jadard_panel_desc` contains mode, lane/format settings, init callback, timing quirks, and DSI mode flags.
- `struct jadard` stores the DRM panel, DSI device, descriptor, orientation, `vdd`/`vccio` regulators, and reset GPIO.
- `jd9365da_switch_page()` selects controller pages with command `0xe0`.
- `jadard_enable_standard_cmds()` unlocks/enables standard command access.
- `jadard_prepare()` enables regulators, optionally sends LP11 NOP, toggles reset, and runs descriptor init.
- `jadard_disable()` sends display off and sleep mode with descriptor delays.
- `jadard_unprepare()` resets and disables regulators.
- Multiple init callbacks encode long page-based vendor scripts for Radxa, Chongzhou, Kingdisplay, Melfas, Anbernic, and Taiguan panels.

## Control Flow

Probe matches compatibles including Anbernic top/bottom displays, `chongzhou,cz101b4001`, `kingdisplay,kd101ne3-40ti`, `melfas,lmfbx101117480`, Radxa displays, and `taiguanck,xti05101-01a`. Default DSI flags are video burst with no EOT unless the descriptor overrides them. Most descriptors are 800x1280 4-lane RGB888 panels; the Anbernic descriptor is 640x480 with negative sync and non-continuous clock/LPM flags. Disable handles DCS off/sleep; unprepare handles reset and regulators.

## State And Persistence

No persistent storage is used. The driver caches descriptor selection, orientation, and resource handles. Panel register state is volatile and reloaded from the init callback during prepare. Anbernic top/bottom behavior is selected through a compatible check at init time.

## Dependencies And Integration Points

Dependencies are DRM panel, MIPI DSI multi-context helpers, DT OF matching/orientation, regulators, reset GPIO, and optional backlight. The connector gets fixed mode data and panel orientation from callbacks.

## Risks

`jadard_prepare()` can return after regulator or DSI-command failures without disabling already enabled rails. The long vendor scripts are opaque and panel-revision sensitive. Timing quirks are descriptor-specific and can cause intermittent boot failures if reused on the wrong board. DSI command errors surface mainly through multi-context return values.

## Test Signals

Verify OF match selection, DSI lane/mode flags, regulator/reset sequencing, preferred mode timing and size, cold boot, blank/unblank, suspend/resume, and Anbernic top/bottom differences. Check logs for accumulated DSI command errors.
