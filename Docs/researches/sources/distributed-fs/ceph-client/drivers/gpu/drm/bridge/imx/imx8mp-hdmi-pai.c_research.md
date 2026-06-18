# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pai.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pai.c

## Purpose

This component driver wires the i.MX8MP HDMI Parallel Audio Interface into the DW HDMI platform data so DW HDMI can enable and disable audio through SoC-specific registers.

## Important APIs, Types, And Functions

`struct imx8mp_hdmi_pai` stores regmap and device. `imx8mp_hdmi_pai_enable()` programs watermarks, channel count, IEC958 or PCM field selection, and starts PAI. `imx8mp_hdmi_pai_disable()` stops it. `imx8mp_hdmi_pai_bind()` maps registers, creates clocked MMIO regmap, fills `dw_hdmi_plat_data` audio hooks, and enables runtime PM.

## Control Flow

Probe registers a component. The HDMI TX master calls bind through `component_bind_all()`, passing DW HDMI platform data. Audio enable resumes runtime PM, writes extended control and field selection based on channel/width/IEC958 parameters, then sets the enable bit. Disable clears enable and releases runtime PM.

## State And Persistence Behavior

State is in regmap, device pointer, and platform data callbacks. Audio hardware state is active only between DW HDMI audio enable and disable. No persistent storage exists.

## Dependencies And Integration Points

It depends on component framework, DW HDMI platform hooks, regmap MMIO with `apb` clock, runtime PM, and ALSA IEC958 bit definitions.

## Risks And Test Signals

Risks include width assumptions limited to 24/32-bit PCM, ignoring runtime PM failure by silently returning from enable, and relying on master bind ordering. Test signals are HDMI audio playback for PCM and IEC958, runtime PM usage counts balancing, and component bind with HDMI TX.
