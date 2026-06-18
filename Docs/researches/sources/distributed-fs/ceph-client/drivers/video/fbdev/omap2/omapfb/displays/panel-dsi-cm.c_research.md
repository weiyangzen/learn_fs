# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-dsi-cm.c

## Purpose
`panel-dsi-cm.c` implements a generic DSI command-mode panel for OMAP2 DSS fbdev. It manages DSI virtual-channel setup, DCS sleep/display/backlight commands, manual updates, TE synchronization, ULPS idle power state, memory reads, sysfs diagnostics, and reset recovery.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores DSS display, upstream DSI source, timings, mutex, backlight device, reset/TE GPIOs, pin config, enabled/TE/ULPS state, DSI channel, update atomic, and delayed works.
- DCS helpers `dsicm_dcs_read_1()`, `dsicm_dcs_write_0()`, and `dsicm_dcs_write_1()` wrap upstream DSI ops.
- Power sequencing uses `dsicm_hw_reset()`, `dsicm_sleep_out()`, `dsicm_power_on()`, `dsicm_power_off()`, and `dsicm_panel_reset()`.
- ULPS flow uses `dsicm_enter_ulps()`, `dsicm_exit_ulps()`, `dsicm_wake_up()`, and `dsicm_ulps_work()`.
- Update flow uses `dsicm_update()`, `dsicm_te_isr()`, `dsicm_te_timeout_work_callback()`, and `dsicm_framedone_cb()`.
- Sysfs attributes expose DSI error count, hardware revision, ULPS state, and ULPS timeout.
- `dsicm_ops` registers display operations including manual update, sync, TE control, and memory read.

## Control Flow
Probe requires OF, finds the upstream DSI source, seeds fixed 864x480 timings, registers the DSS display with manual-update and tear-elimination caps, initializes locks/work, requests reset and optional TE GPIO, optionally registers DSI backlight, resets the panel, and creates sysfs files. Connect forwards DSI connect, requests a virtual channel, and maps it to hard-coded target VC ID 0. Enable locks the panel, bus-locks DSI, powers on the panel, and marks active. Power-on configures DSI pins/config, enables DSI, resets hardware, leaves HS off for commands, exits sleep, reads ID, configures brightness/display control/pixel format/display-on/TE, enables video output, then enables HS mode.

Manual update wakes from ULPS, sets the full update window, and either waits for external TE IRQ before starting `in->ops.dsi->update()` or starts immediately. The DSI bus lock is intentionally held until frame-done callback or TE timeout. Disable cancels ULPS work, wakes if needed, powers off, disables DSI, and marks disabled. Memory read sets a DCS read window and loops reading small packets until the requested RGB888 data is collected or interrupted.

## State And Persistence
State is per platform device and protected mostly by `ddata->lock` plus upstream DSI bus locks. `do_update` coordinates TE IRQ update start. `ulps_enabled` and delayed ULPS work implement runtime low-power state. No state persists beyond driver lifetime.

## Dependencies And Integration Points
The driver depends on OMAP DSS DSI ops, MIPI DCS constants, GPIO descriptors, IRQs, workqueues, backlight class, sysfs, and OF graph lookup. It registers as an OMAP DSS DSI display.

## Risks
Several configuration fields (`use_dsi_backlight`, `pin_config`, `ulps_timeout`) are not parsed in the visible probe path, so defaults may disable intended features. TE update flow holds the DSI bus lock across async completion; missed frame-done or TE timeout bugs can stall the bus. Error paths after `omapdss_register_display()` may return without unregistering the display. Reset GPIO polarity comments indicate compatibility with incorrect DTS polarity. Memory reads use very small packet sizes and can be slow.

## Test Signals
Signals include successful display registration, DSI VC allocation, panel ID sysfs read, DSI error sysfs read, enable/disable with DCS sleep/display transitions, manual update completion with and without TE GPIO, TE timeout recovery, ULPS sysfs toggling, backlight writes when enabled, and memory-read correctness.
