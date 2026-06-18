# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-analog-tv.c

## Purpose
`connector-analog-tv.c` implements a generic OF-only analog TV connector display for the OMAP2 DSS fbdev stack, supporting S-video and composite connector compatibles.

## Important APIs, Types, And Functions
- `struct panel_drv_data` embeds an `omap_dss_device`, stores upstream `in`, device pointer, current timings, and polarity flag.
- `tvc_pal_timings` defines default PAL-like interlaced 720x574 timings.
- `tvc_driver` supplies connect/disconnect, enable/disable, timings, resolution, and WSS operations.
- Probe finds the upstream source via OF endpoint and registers the display as `OMAP_DISPLAY_TYPE_VENC`.

## Control Flow
Probe allocates state, finds the first endpoint source, initializes default timings, fills `dssdev`, and calls `omapdss_register_display()`. Enable requires connection, programs timings, optionally sets composite type and output polarity for non-DT use, enables upstream ATV output, and marks state active. Disable calls upstream disable and marks state disabled. Remove unregisters, disables/disconnects, and drops the source reference.

## State And Persistence
Per-device state stores current timings and connection state in the embedded DSS device. No persistent storage.

## Dependencies And Integration Points
The driver depends on OF graph helpers, OMAP DSS ATV ops, WSS get/set passthrough, and `omapdss_register_display()`.

## Risks
The probe rejects non-OF devices, while enable still has a legacy non-OF branch that is unreachable through this probe. WSS and timing operations assume `in->ops.atv` is valid. Only default PAL timings are provided.

## Test Signals
Device-tree nodes compatible with `omapdss,svideo-connector` or `omapdss,composite-video-connector` should register a VENC display, connect to the upstream source, enable with PAL timings, and pass WSS operations through.
