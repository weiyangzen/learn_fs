<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.h

## Purpose
This header defines the i915 MIPI DSI encoder state structure, DSI host wrapper, DSI mode/dual-link constants, iteration helpers, and common DSI function declarations.

## Important APIs, Types, and Functions
`struct intel_dsi` embeds `struct intel_encoder` and stores DSI hosts, IO wakerefs, optional GPIOs, attached connector, port/PHY mask, virtual channel, operation mode, lane count, I2C bus, pixel format, video mode, packet/clock flags, escape clock, dual-link layout, timing registers, pixel clock, burst ratio, and panel/backlight delays. `struct intel_dsi_host` wraps `mipi_dsi_host`, back-points to `intel_dsi`, stores a port, and holds the manually allocated `mipi_dsi_device`.

Inline helpers include `to_intel_dsi_host()`, `for_each_dsi_port()`, `for_each_dsi_phy()`, `enc_to_intel_dsi()`, `is_vid_mode()`, `is_cmd_mode()`, and `intel_dsi_encoder_ports()`.

## Control Flow
There is no executable flow beyond inline casts and mode predicates. The state layout is populated by VBT parsing, platform DSI init code, and panel power/backlight paths, then consumed by encoder enable/disable and MIPI sequence execution.

## State and Persistence Behavior
`struct intel_dsi` is persistent encoder state. Several fields are VBT-derived policy, while `panel_power_off_time` records runtime timing for power-cycle enforcement. The union of `ports` and `phys` reflects platform split between VLV-style ports and ICL-style PHYs.

## Dependencies and Integration Points
The header depends on DRM CRTC/MIPI DSI definitions and `intel_display_types.h`. It integrates with VBT parsing, DCS backlight, panel mode helpers, platform DSI encoders, shutdown, and MIPI command execution.

## Risks
Misinterpreting `ports` versus `phys` can target the wrong link. Many timing fields are in byte clocks or milliseconds depending on origin; unit confusion affects panel bring-up. The manual DSI host/device approach requires consistent lifetime management outside standard driver registration.

## Test Signals
Signals include DSI encoder initialization on single and dual-link panels, correct per-port sequence execution, video and command mode bring-up, GPIO/backlight timing, and compile coverage for all inline helpers across VLV and ICL paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.h -->
