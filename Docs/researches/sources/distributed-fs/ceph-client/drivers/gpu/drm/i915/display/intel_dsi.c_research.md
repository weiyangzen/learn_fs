<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.c

## Purpose
This file provides common MIPI DSI helpers for panel power-cycle timing, bitrate/TLPX calculation, mode validation, host/device allocation, and panel orientation selection.

## Important APIs, Types, and Functions
Exported functions are `intel_dsi_wait_panel_power_cycle()`, `intel_dsi_shutdown()`, `intel_dsi_bitrate()`, `intel_dsi_tlpx_ns()`, `intel_dsi_get_modes()`, `intel_dsi_mode_valid()`, `intel_dsi_host_init()`, and `intel_dsi_get_panel_orientation()`.

## Control Flow
Power-cycle handling compares boottime against `panel_power_off_time` and sleeps until `panel_pwr_cycle_delay` is satisfied. Bitrate computes pixel clock times bits-per-pixel divided by lane count, with a fallback for invalid format. Mode validation checks panel mode validity, fixed-mode dotclock against max CDCLK dotclock, and maximum plane size. Host initialization manually allocates a `mipi_dsi_host` and `mipi_dsi_device` because the driver uses the DRM MIPI DSI framework as a library rather than registering normal device-model hosts.

## State and Persistence Behavior
The helper updates no persistent state except allocated DSI host/device objects returned to caller-owned `intel_dsi`. Panel timing state comes from `intel_dsi` fields populated by VBT parsing. Orientation is selected from panel VBT DSI orientation, then global VBT orientation, then normal.

## Dependencies and Integration Points
It integrates with DRM MIPI DSI helpers, `intel_panel` mode helpers, CDCLK limits, display max-plane-size validation, DSI shutdown hooks, and VBT-derived `struct intel_dsi` state.

## Risks
Incorrect lane count, pixel format, or pclk produces bad bitrate calculations and PHY programming downstream. The manually allocated DSI device bypasses normal driver-model initialization, so callers must manage lifetime carefully. Power-cycle delay is only as good as `panel_power_off_time` updates elsewhere.

## Test Signals
Signals include DSI panel modes enumerating correctly, invalid high-clock modes rejected, panel shutdown/resume respecting power-cycle delay, bitrate/TLPX values matching VBT expectations, orientation property matching VBT, and leak checks for host/device allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.c -->
