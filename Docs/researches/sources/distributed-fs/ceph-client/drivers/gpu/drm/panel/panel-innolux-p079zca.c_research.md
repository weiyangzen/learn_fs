# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-innolux-p079zca.c

## Purpose

This DRM MIPI DSI panel driver covers Innolux `p079zca` and `p097pfg` panels. It supports one simpler 768x1024 panel and one 1536x2048 panel with a long vendor register initialization sequence.

## Important APIs, Types, And Functions

- `struct panel_desc` stores fixed mode, bpc, physical size, DSI settings, optional init callback, regulator names, and delays.
- `struct innolux_panel` stores the DRM panel, DSI link, descriptor, bulk regulators, and optional enable GPIO.
- `innolux_panel_prepare()` enables supplies, toggles enable, runs optional init, exits sleep, waits, and sets display on.
- `innolux_panel_unprepare()` sends display off/sleep, applies delays, lowers enable, and disables regulators.
- `innolux_panel_write_multi()` wraps generic writes and adds a DCS NOP after each write to avoid missed commands.
- `innolux_p097pfg_init()` sends the multi-page vendor register script.
- `innolux_panel_probe()` applies descriptor DSI settings, adds the panel, and attaches.

## Control Flow

OF match data selects `innolux,p079zca` or `innolux,p097pfg`. The p079zca descriptor uses one `power` regulator and no custom init callback. The p097pfg descriptor uses `avdd` and `avee`, a 1536x2048 mode, and the register-dump init script. Prepare powers, enables, initializes, exits sleep, and displays on. Unprepare sends DCS shutdown before powerdown. One preferred descriptor mode is exposed.

## State And Persistence

No persistent or discovered state is used. Descriptor and resource handles are the only software state. Vendor register state is volatile and reprogrammed on prepare for p097pfg.

## Dependencies And Integration Points

The driver integrates with DRM panel, MIPI DSI, OF matching, regulator bulk APIs, optional enable GPIO, and optional panel backlight. It expects 4-lane RGB888 video mode with sync pulse and low-power command transfers.

## Risks

The p097pfg init sequence comes from a register dump rather than manufacturer sequencing, so panel revisions are risky. The NOP-after-write behavior is empirical and should not be removed casually. Optional enable GPIO errors are ignored after debug logging, which can mask DT mistakes. Timing values should be validated per panel.

## Test Signals

Confirm DSI attach, regulator names per compatible, enable GPIO behavior, one preferred mode, and reliable cold boot/resume. On p097pfg, verify that the full page-switch script is accepted without blank output or gamma/mapping problems.
