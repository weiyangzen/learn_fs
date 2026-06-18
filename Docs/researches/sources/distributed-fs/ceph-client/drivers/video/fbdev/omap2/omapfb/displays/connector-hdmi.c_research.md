# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/connector-hdmi.c

## Purpose
`connector-hdmi.c` implements a generic OF HDMI connector display for OMAP2 DSS fbdev. It passes HDMI operations to an upstream HDMI output and optionally uses an HPD GPIO for detection.

## Important APIs, Types, And Functions
- `hdmic_default_timings` defines default 640x480 HDMI timings.
- `struct panel_drv_data` stores DSS device, upstream source, device pointer, timings, and optional HPD GPIO.
- `hdmic_driver` implements connect/disconnect, enable/disable, timing operations, EDID, detect, HDMI/DVI mode, and AVI infoframe forwarding.

## Control Flow
Probe requires OF, requests optional `hpd` GPIO, names it, finds the upstream source endpoint, initializes timings, registers an HDMI display, and releases the source on failure. Enable requires connection, sets timings, calls upstream enable, and marks state active. Detection reads HPD GPIO if present, else forwards to upstream HDMI detect.

## State And Persistence
The driver stores current timings and optional HPD descriptor per device. No persistent state or EDID cache is kept.

## Dependencies And Integration Points
It depends on GPIO descriptors, OF graph helpers, DRM HDMI infoframe/EDID types, and OMAP DSS HDMI ops.

## Risks
If HPD GPIO polarity is wrong in DT, detection is inverted. EDID and infoframe calls assume upstream ops exist. No hotplug interrupt handling is implemented here; consumers must poll or rely on higher layers.

## Test Signals
A valid `omapdss,hdmi-connector` node should register an HDMI display, report HPD accurately, read EDID through upstream ops, set HDMI mode/infoframes, and enable/disable cleanly.
