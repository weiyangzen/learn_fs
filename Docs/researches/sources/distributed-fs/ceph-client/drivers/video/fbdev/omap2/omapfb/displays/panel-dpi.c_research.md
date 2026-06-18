# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-dpi.c

## Purpose
`panel-dpi.c` implements a generic OF-described DPI panel for the OMAP2 DSS fbdev stack. It reads display timings from device tree, forwards DPI operations upstream, and controls an optional enable GPIO.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores DSS display, upstream DPI source, data-line count, video timings, and optional enable GPIO.
- `panel_dpi_probe_of()` reads the `panel-timing` node via `of_get_display_timing()`, converts it to `omap_video_timings`, requests optional enable GPIO, and finds the upstream source.
- `panel_dpi_ops` supplies display connect/disconnect, enable/disable, timing methods, and resolution.

## Control Flow
Probe requires OF, allocates state, parses panel timing and source endpoint, fills the DSS display, and registers it. Enable requires a connection, sets data lines if nonzero, sets timings, enables upstream DPI, asserts enable GPIO, and marks active. Disable clears GPIO, disables upstream, and marks disabled. Remove unregisters, disables/disconnects, and releases the upstream source.

## State And Persistence
Timings and GPIO/source references are per-device runtime state. No persistent storage.

## Dependencies And Integration Points
The driver depends on OF display timing parsing, GPIO descriptors, OMAP DSS DPI ops, and `omapdss_register_display()`.

## Risks
`data_lines` is not parsed, so data-line configuration remains zero unless extended. Enable GPIO is optional but `gpiod_set_value_cansleep(NULL, ...)` is tolerated by gpiod APIs; behavior depends on kernel semantics. Bad DT timing values are only caught by upstream `check_timings`.

## Test Signals
Valid DT `panel-timing` should create a DPI display with expected resolution/timing, assert enable GPIO on active state, and pass timing checks through upstream DPI.
