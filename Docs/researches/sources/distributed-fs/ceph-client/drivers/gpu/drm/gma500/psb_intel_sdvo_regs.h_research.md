
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_sdvo_regs.h

## Purpose
`psb_intel_sdvo_regs.h` defines the SDVO command protocol, I2C register addresses, response statuses, packed request/reply structures, output flag bits, TV format maps, timing layouts, enhancement controls, LVDS panel data, power states, and HDMI command IDs used by the GMA500 SDVO driver.

## Important APIs, Types, And Functions
The header exports output flags such as `SDVO_OUTPUT_TMDS0`, `SDVO_OUTPUT_RGB0`, `SDVO_OUTPUT_CVBS0`, `SDVO_OUTPUT_SVID0`, `SDVO_OUTPUT_LVDS0`, and the corresponding second-channel flags. Important packed types include `struct psb_intel_sdvo_caps`, `struct psb_intel_sdvo_dtd`, `struct psb_intel_sdvo_pixel_clock_range`, `struct psb_intel_sdvo_preferred_input_timing_args`, `struct psb_intel_sdvo_get_trained_inputs_response`, `struct psb_intel_sdvo_in_out_map`, `struct psb_intel_sdvo_tv_format`, SDTV/HDTV resolution request/reply structures, `struct psb_sdvo_panel_power_sequencing`, `struct psb_intel_sdvo_enhancements_reply`, `struct psb_intel_sdvo_enhancement_limits_reply`, and `struct psb_intel_sdvo_encode`.

Command constants cover device caps, firmware, trained inputs, active outputs, input/output maps, hotplug, target input/output, timing get/set, preferred input timing generation, pixel clock ranges, clock multipliers, TV format/resolution, encoder and display power, panel power sequencing, backlight/ambient light, enhancement get/set commands, DDC bus switching, and HDMI encode/colorimetry/audio/hardware buffer operations.

## Control Flow
The header has no executable flow. `psb_intel_sdvo.c` uses the I2C register constants to marshal arguments, writes one of the `SDVO_CMD_*` opcodes, reads `SDVO_I2C_CMD_STATUS`, and interprets the response bytes by casting them into the packed structures defined here.

## State And Persistence
The constants describe state stored inside the SDVO device firmware and encoder hardware: active output masks, selected target input/output, DTD timing data, clock multiplier, TV format, power state, panel sequencing, backlight, ambient light, enhancement levels, DDC bus switch, HDMI encode mode, colorimetry, audio state, and infoframe buffer state. The header itself stores no state.

## Dependencies And Integration Points
It depends on kernel integer typedefs and packed bitfield behavior. It is paired directly with `psb_intel_sdvo.c` and indirectly with the DRM connector property layer, EDID/DDC code, and GMA500 SDVO MMIO definitions in `psb_intel_reg.h`.

## Risks
The packed bitfield structures depend on compiler layout matching the SDVO firmware protocol. Some comments contain historical typos, and the HDMI command set is more complete than the implementation, which can make apparent support misleading. Command status handling in users must account for `PENDING`, `TARGET_NOT_SPECIFIED`, and unsupported responses. TV and HDTV resolution structures are dense bitmaps where index ordering must match the driver's mode table.

## Test Signals
Validation should confirm `BUILD_BUG_ON` structure sizes in the implementation remain true, device capabilities parse correctly, timing DTD round-trips match DRM mode fields, TV format bitmaps produce the intended property names and modes, enhancement max/current reads map to the right properties, and unsupported command statuses are handled without leaving the SDVO device in a partially programmed state.
