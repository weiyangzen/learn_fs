<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_hdmi.c

## Purpose

This file implements Cedarview HDMI/TMDS connector and encoder support for ports exposed through SDVOB/SDVOC register names. It handles DDC-based detection, HDMI audio capability tracking, port control programming, scaling property changes, and DRM object creation.

## Important APIs, Types, And Functions

The exported function is `cdv_hdmi_init()`. Important local pieces are `struct mid_intel_hdmi_priv`, `cdv_hdmi_mode_set()`, `cdv_hdmi_dpms()`, `cdv_hdmi_save()`, `cdv_hdmi_restore()`, `cdv_hdmi_detect()`, `cdv_hdmi_set_property()`, `cdv_hdmi_get_modes()`, `cdv_hdmi_mode_valid()`, and cleanup/helper callback tables.

## Control Flow

Initialization allocates encoder, connector, and private state; picks GPIOE/DDI0 for SDVOB or GPIOD/DDI1 for SDVOC; creates a DDC bus; initializes a DVID connector and TMDS encoder; attaches them; installs helpers; disables interlace/doublescan; and attaches the scaling property. Detection reads EDID, marks connected if the input is digital, and derives HDMI sink/audio flags. Mode set writes sync polarity, pipe select, audio enable, and null-packet bits before DPMS toggles `HDMIB_PORT_EN`. Scaling property changes update the connector property and either call full mode set or encoder mode-set depending on center/no-scale transition.

## State And Persistence

Private state stores the HDMI register offset, saved register value, sink/audio flags, and device pointer. Hardware state persists in the SDVOB/SDVOC HDMI control register and DDC GPIO/I2C state. Connector properties persist until changed by userspace.

## Dependencies And Integration Points

It integrates DRM EDID helpers, GMA I2C, simple encoder creation, shared GMA encoder helpers, Cedarview property helpers, and output detection in `cdv_output_init()`.

## Risks And Test Signals

Risks include connector type `DVID` despite HDMI semantics, no HPD status register use in detection beyond polling setup, mode clock cap hardcoded to 165 MHz, returning `MODE_CLOCK_HIGH` for clocks below 20 MHz, and scaling property paths using legacy helper mode setting. Test signals are EDID detection on both SDVOB/SDVOC, HDMI audio EDID, DPMS on/off, mode validation around 20 MHz and 165 MHz, scaling property changes, and cleanup after DDC or DRM init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_hdmi.c -->
