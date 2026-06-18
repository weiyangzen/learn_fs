# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/g4x_hdmi.c

## Purpose
`g4x_hdmi.c` implements legacy HDMI encoder support for G4x, ILK, SNB, IVB, VLV, and CHV platforms, while newer HSW+ DDI hardware is handled elsewhere. It configures HDMI/SDVO-style registers, infoframes, audio presence, hotplug behavior, platform-specific PHY/enable sequences, connector atomic checks, and encoder initialization via `g4x_hdmi_init()`.

## Important APIs, Types, and Functions
`intel_hdmi_prepare()` builds and writes the HDMI control value: TMDS output, sync polarity, limited color range, 8/12 bpc format, HDMI/DVI mode, and pipe select. `intel_hdmi_get_hw_state()` asks `intel_sdvo_port_enabled()` under the encoder power domain. `g4x_hdmi_compute_config()` marks PCH encoder usage and computes `has_hdmi_sink`; on G4x, `g4x_compute_has_hdmi_sink()` selects only one active HDMI port to transmit infoframes/audio. `intel_hdmi_get_config()` reconstructs output type, sync flags, HDMI sink state, infoframe state, audio, limited range, dotclock, lane count, GCP, AVI/SPD/vendor infoframes, and audio codec config.

Enable/disable paths are platform-specific. `g4x_hdmi_enable_port()` sets `SDVO_ENABLE`. `ibx_enable_hdmi()` writes the enable bit twice and toggles for a 12bpc pixel-repeat workaround. `cpt_enable_hdmi()` implements `WaEnableHDMI8bpcBefore12bpc` using `TRANS_CHICKEN1`. `intel_disable_hdmi()` clears enable, applies the IBX pipe-A workaround shared with DP-port routing, disables infoframes, and disables dual-mode TMDS output. VLV/CHV pre-enable paths program DPIO PHY signal levels, infoframes, port enable, lane readiness, and CL2 override release.

`g4x_hdmi_audio_enable()` and `_disable()` wrap HDMI audio presence bits and codec callbacks. `intel_hdmi_hotplug()` requests retry detection when live state is unreliable. `g4x_hdmi_connector_atomic_check()` adds all enabled HDMI connectors to the atomic state on G4x so the single infoframe/audio-capable port can be selected consistently. `g4x_hdmi_init()` validates the port, allocates digital port and connector objects, initializes the DRM encoder, installs callbacks, sets power domain, pipe mask, cloneability, HPD pin, infoframe helpers, and calls `intel_hdmi_init_connector()`.

## Control Flow and State
Atomic commit computes sink/audio/infoframe decisions first, then pre-enable writes static HDMI register state and infoframes, enable performs platform-specific port activation, and audio hooks set codec state. Disable paths clear the port and infoframes after or during platform-specific post-disable sequencing. Persistent software state lives in `dig_port->hdmi.hdmi_reg`, encoder callback fields, connector state, and atomic `intel_crtc_state` flags; hardware state lives in HDMI/SDVO registers and infoframe storage.

## Dependencies and Integration Points
The file integrates with DRM atomic helpers, i915 audio, infoframe, SDVO, hotplug, PCH display, DPIO PHY, display power, and register access layers. `intel_display.c` calls `g4x_hdmi_init()` for platform-supported HDMI ports. `g4x_hdmi_connector_atomic_check()` is exposed through the header for connector code.

## Risks and Test Signals
Main risks are platform-specific enable ordering, shared DP/HDMI PCH routing workarounds, G4x single-infoframe behavior, unreliable HPD live state, 12bpc and pixel-repeat workarounds, and VLV/CHV PHY constants. Test signals include HDMI and DVI modesets, audio enable/disable, infoframe readback, hotplug retry behavior, cloning on G4x, suspend/resume state readout, absence of FIFO underruns around IBX workarounds, and successful 8bpc/12bpc/pixel-repeat modes.
