# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-dvi.c

## Purpose
`connector-dvi.c` implements a generic OF DVI connector display for OMAP2 DSS fbdev. It forwards DVI connect/timing/enable calls and optionally performs DDC/EDID reads through an I2C adapter.

## Important APIs, Types, And Functions
- `dvic_default_timings` provides 640x480 DVI timings and signal polarity defaults.
- `struct panel_drv_data` stores DSS device, upstream source, current timings, and optional DDC I2C adapter.
- `dvic_ddc_read()` performs a DDC segment read with three retries on `-EAGAIN`.
- `dvic_read_edid()` reads base EDID and one optional extension block.
- `dvic_detect()` uses DDC if available, otherwise reports connected.
- `dvic_driver` exposes DSS display operations.

## Control Flow
Probe requires OF, allocates state, finds the upstream source, optionally resolves `ddc-i2c-bus`, initializes default timings, registers a DVI display, and cleans up references on failure. Enable requires connection, sets timings on upstream DVI ops, enables upstream output, and sets active state. Remove unregisters, disables/disconnects, drops the upstream device, and releases the I2C adapter.

## State And Persistence
Current timings and adapter/source references live in per-device memory. EDID reads are on-demand and not cached.

## Dependencies And Integration Points
The file depends on I2C, DRM EDID constants, OF graph/phandle parsing, and OMAP DSS DVI ops.

## Risks
Only one EDID extension block is read. `detect()` returns true without DDC, which may report a disconnected passive connector as present. Timing mutation is passed through to upstream ops and stored locally. Probe defers if DDC adapter is not ready.

## Test Signals
Expected signals include DVI display registration, optional successful DDC EDID reads from address `DDC_ADDR`, correct `detect()` behavior with/without DDC, and enable/disable propagation to upstream DVI output.
