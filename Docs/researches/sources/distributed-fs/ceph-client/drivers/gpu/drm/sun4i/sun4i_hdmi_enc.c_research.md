<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_enc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_enc.c

## Purpose

`sun4i_hdmi_enc.c` implements the legacy Allwinner A10/A10s/A31 HDMI encoder, connector, hotplug polling, EDID retrieval, CEC pin glue, component binding, and SoC variant data. It drives the HDMI MMIO block directly and creates the internal TMDS clock and DDC I2C adapter used by the DRM HDMI connector.

## Important APIs, Types, And Functions

Key entry points are `sun4i_hdmi_bind()`, `sun4i_hdmi_unbind()`, `sun4i_hdmi_enable()`, `sun4i_hdmi_disable()`, `sun4i_hdmi_get_modes()`, `sun4i_hdmi_connector_detect()`, and `sun4i_hdmi_connector_clock_valid()`. The variant tables `sun4i_variant`, `sun5i_variant`, and `sun6i_variant` encode pad, PLL, TMDS divider, reset, DDC clock, and regmap-field differences. DRM integration is through encoder helper funcs, connector funcs, `drmm_connector_hdmi_init()`, and `drm_atomic_helper_connector_hdmi_update_infoframes()`.

## Control Flow

Probe adds a component. Bind allocates `struct sun4i_hdmi`, maps registers, deasserts optional reset, enables bus/mod clocks, creates a regmap, registers the TMDS clock, creates the HDMI DDC adapter, optionally gets an external `ddc-i2c-bus`, initializes the DRM encoder/connector, configures optional CEC, and attaches encoder to connector. Atomic enable sets mod/TMDS rates from connector HDMI state, reprograms pad/timing/polarity/infoframe registers, enables the TMDS clock, and turns on video output. Disable clears video enable and disables TMDS.

## State And Persistence Behavior

Persistent state lives in `struct sun4i_hdmi`: MMIO base, regmap, clocks, reset, connector, encoder, CEC adapter, internal/external DDC adapters, and variant pointer. Hardware state persists in pad, PLL, timing, packet, HPD, CEC, and video-control registers until disabled or reset.

## Dependencies And Integration Points

It depends on DRM atomic HDMI helpers, EDID/DDC helpers, CEC pin ops, Linux component framework, clocks, resets, regmap, platform resources, `sun4i_hdmi_i2c_create()`, and `sun4i_tmds_create()`. It integrates with TCON channel 1 through possible CRTCs from OF graph and with `sun4i_tcon_mode_set()` via the TMDS encoder type.

## Risks And Test Signals

Risks include incomplete HDMI VSI/clear-infoframe support, no HPD IRQ so polling latency is expected, fragile undocumented pad/PLL values, clock rounding limited to 165 MHz, and cleanup paths that must balance clocks, DDC adapters, CEC, and resets. Test by probing all compatibles, EDID over internal and external DDC, HPD connect/disconnect, HDMI vs DVI sinks, CEC pin toggling, mode validation around 165 MHz, and enable/disable/suspend cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi_enc.c -->
