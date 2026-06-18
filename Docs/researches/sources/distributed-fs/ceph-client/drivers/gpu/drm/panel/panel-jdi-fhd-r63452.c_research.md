# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-jdi-fhd-r63452.c

## Purpose

This is a DRM MIPI DSI panel driver for a JDI FHD R63452 command-mode panel. It was generated from downstream Android panel data and exposes one fixed 1080x1920 mode.

## Important APIs, Types, And Functions

- `struct jdi_fhd_r63452` stores the DRM panel, DSI device, and reset GPIO.
- `jdi_fhd_r63452_reset()` performs the reset pulse sequence.
- `jdi_fhd_r63452_on()` sends the vendor/DCS init sequence, TE enable, address window, brightness/control-display settings, display on, sleep exit, and extra page writes.
- `jdi_fhd_r63452_off()` sends vendor setup, display off, sleep mode, and delay.
- `jdi_fhd_r63452_prepare()` resets and powers the panel up through DSI commands.
- `jdi_fhd_r63452_unprepare()` attempts DSI shutdown, asserts reset, and returns success.
- `jdi_fhd_r63452_probe()` configures 4-lane RGB888 DSI video burst with non-continuous clock, finds backlight, adds the panel, and attaches.

## Control Flow

The DSI driver matches `jdi,fhd-r63452`. Probe configures DSI settings and registers the panel. Prepare controls reset and the DCS/vendor command setup; no regulators are handled in this file. Unprepare attempts display-off/sleep and asserts reset regardless. `get_modes()` exposes the fixed preferred 1080x1920 mode and 64 mm by 114 mm size.

## State And Persistence

No persistent state is kept. Brightness is initialized to `0x00ff`, while ongoing backlight policy is external through `drm_panel_of_backlight()`. Register state is volatile and recreated on prepare.

## Dependencies And Integration Points

Dependencies are DRM panel, MIPI DSI DCS/generic helpers, reset GPIO, DT OF matching, and optional OF backlight. The init sequence is inherited from downstream panel data.

## Risks

There is no regulator handling, so board power must be supplied externally. Shutdown DSI errors are ignored by design in unprepare. The on sequence sets display on before exit sleep, which is unusual and should not be reordered without hardware evidence. LPM mode flag changes can interact with host expectations.

## Test Signals

Check DSI attach, reset timing, one preferred 1080x1920 mode, backlight lookup, clean prepare/unprepare, TE behavior, address-window coverage, and resume reliability.
