<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.c

## Purpose
This file implements panel backlight control through MIPI DCS commands for DSI panels whose VBT requests `INTEL_BACKLIGHT_DSI_DCS`.

## Important APIs, Types, and Functions
The public entry point is `intel_dsi_dcs_init_backlight_funcs()`, which installs `dcs_bl_funcs`. Internal callbacks are `dcs_setup_backlight()`, `dcs_enable_backlight()`, `dcs_disable_backlight()`, `dcs_set_backlight()`, and `dcs_get_backlight()`. It uses DCS commands `GET/SET_DISPLAY_BRIGHTNESS`, `GET/WRITE_CONTROL_DISPLAY`, and `WRITE_POWER_SAVE`.

## Control Flow
Initialization rejects non-DCS backlight types and non-DSI encoders, then assigns panel backlight callbacks. Setup derives max brightness from VBT precision bits or 8-bit default and initializes the level to max. Set/get iterate the configured backlight ports. Enable sets display-control bits, enables CABC power-save mode on CABC ports, then writes brightness. Disable writes brightness zero, disables CABC, reads display-control, clears backlight/display-dimming/brightness-control bits, and writes it back.

## State and Persistence Behavior
The callback table is persistent in `panel->backlight.funcs`; current brightness lives in generic panel backlight state. DCS writes mutate panel-internal state over the DSI link. `dcs_set_backlight()` temporarily clears `MIPI_DSI_MODE_LPM` and restores original mode flags.

## Dependencies and Integration Points
The file depends on DRM MIPI DSI helpers, MIPI DCS command definitions, `intel_panel` backlight infrastructure, VBT-selected backlight/CABC port masks, and the attached DSI encoder/device objects.

## Risks
Byte order differs between get and set paths for 16-bit brightness and should be validated against panel expectations. DCS command failures are not deeply propagated in callbacks. Port masks must match initialized hosts. Clearing LPM changes transaction mode temporarily, so restoration must remain exception-safe.

## Test Signals
Signals include DCS backlight setup on VBT-marked panels, brightness read/write at 8-bit and wider precision, enable/disable sequencing on dual-link panels, CABC command behavior, no warnings for non-DSI encoders, and visible backlight changes without panel command errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.c -->
