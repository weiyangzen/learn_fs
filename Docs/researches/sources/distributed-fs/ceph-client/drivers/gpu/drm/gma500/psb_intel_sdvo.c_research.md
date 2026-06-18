
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_sdvo.c

## Purpose
`psb_intel_sdvo.c` implements SDVO encoder and connector support for the GMA500 DRM driver. It discovers an SDVO device over the GMBUS/I2C control channel, creates DRM connectors for TMDS/DVI/HDMI, VGA, TV, and LVDS outputs advertised by the SDVO device, handles DDC proxying, validates and programs modes, controls DPMS, and exposes supported TV/LVDS enhancement properties.

## Important APIs, Types, And Functions
The central private types are `struct psb_intel_sdvo`, which embeds `struct gma_encoder` and stores the SDVO register, I2C adapter, DDC proxy, target address, capabilities, attached outputs, pixel clock limits, HDMI/audio flags, TV/LVDS mode state, pixel multiplier, input DTD, and saved register value; and `struct psb_intel_sdvo_connector`, which embeds `struct gma_connector` and stores per-connector output flags, forced audio state, TV format property, enhancement DRM properties, current/max enhancement values, and margin state.

The exported entry point is `psb_intel_sdvo_init(struct drm_device *dev, int sdvo_reg)`. Major internal helpers include `psb_intel_sdvo_read_byte()`, `psb_intel_sdvo_write_cmd()`, `psb_intel_sdvo_read_response()`, `psb_intel_sdvo_get_value()`, `psb_intel_sdvo_set_value()`, `psb_intel_sdvo_mode_fixup()`, `psb_intel_sdvo_mode_set()`, `psb_intel_sdvo_dpms()`, `psb_intel_sdvo_detect()`, `psb_intel_sdvo_get_modes()`, `psb_intel_sdvo_set_property()`, `psb_intel_sdvo_output_setup()`, connector-specific init routines, and the DDC proxy algorithm.

## Control Flow
Initialization allocates the SDVO encoder, chooses the target I2C address from VBT mappings or SDVOB/SDVOC defaults, selects the GMBUS adapter and speed, registers an I2C DDC proxy, initializes the DRM encoder, probes the first 0x40 SDVO I2C registers to confirm device presence, marks hotplug support, reads device capabilities, creates connectors according to the advertised output flags, selects the DDC bus, targets SDVO input 0, and reads the input pixel clock range.

Command flow writes SDVO arguments into descending `SDVO_I2C_ARG_*` registers, writes the opcode, then polls `SDVO_I2C_CMD_STATUS` up to five times with 15 microsecond delays before reading response bytes. Mode fixup prepares preferred input timing for TV/LVDS and applies the SDVO pixel multiplier. Mode set maps input 0 to the attached output, programs output and input DTDs, selects HDMI or DVI encode mode, sets TV format when needed, sets clock multiplier, composes `SDVOB` or `SDVOC`, selects pipe B when required, optionally enables SDVO audio, and writes both SDVO registers twice to match the BIOS workaround. DPMS disables active outputs and the SDVO port on off, or enables the port, waits two vblanks, checks trained inputs, and re-enables active outputs on on.

Detection asks `GET_ATTACHED_DISPLAYS`, delays for possible TV outputs, filters against the connector output flag, and for TMDS reads EDID through the SDVO DDC proxy and fallback analog DDC to decide HDMI/audio state. Mode enumeration uses EDID for digital/analog, fixed DDC or VBT modes for LVDS, and SDVO TV resolution commands for TV connectors. Property changes update local state, issue SDVO enhancement commands for relevant TV/LVDS properties, and force a CRTC modeset when the encoder is active.

## State And Persistence
Persistent software state lives in the SDVO encoder and connector objects: selected DDC bus, attached output mask, HDMI/audio flags, TV format index, LVDS fixed mode, pixel clock limits, saved SDVO register value, and enhancement property values. Hardware state lives in the SDVO device command register space and GMA500 SDVO MMIO registers. The driver also registers an I2C adapter for the DDC proxy and creates DRM connector/encoder objects that persist until connector or encoder destroy.

## Dependencies And Integration Points
This code depends on DRM KMS helper callbacks, GMA500 wrappers from `psb_drv.h` and `psb_intel_drv.h`, SDVO command definitions from `psb_intel_sdvo_regs.h`, register constants from `psb_intel_reg.h`, GMBUS adapters and VBT mappings in `struct drm_psb_private`, EDID helpers, GMA connector/encoder helpers, and optional hotplug support through `dev_priv->hotplug_supported_mask`.

## Risks
The command protocol is timing-sensitive and assumes register layouts from the SDVO spec. The DDC bus selection has an explicit hard-coded fallback to bus 2, so boards with unusual VBT mappings may fail EDID detection. Several HDMI paths are stubs or disabled, including AVI infoframe programming and HDMI properties, so HDMI sink/audio support is incomplete. The SDVO register write workaround writes both SDVOB and SDVOC twice and preserves only selected bits; mistakes can disturb the other SDVO port. Property changes can trigger full CRTC modesets. LVDS fixed-mode handling depends on EDID or VBT availability.

## Test Signals
Test signals include successful `psb_intel_sdvo_init()` on both SDVOB and SDVOC addresses, correct connector creation for advertised output flags, reliable EDID reads through the DDC proxy and fallback path, mode validation respecting SDVO clock limits and LVDS fixed panel bounds, working DPMS off/on with trained input status, correct TV mode enumeration and enhancement property programming, hotplug events for SDVO status bits, and no regressions in vblank/mode setting after property changes.
