# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-visionox-r66451.c

## Purpose
This driver supports the Visionox R66451 AMOLED DSI panel with Display Stream Compression (DSC). It configures DSC parameters, sends a large vendor initialization sequence, sends PPS during enable, and exposes fixed 1080x2340 timing plus raw DCS brightness.

## Important APIs, Types, And Functions
`struct visionox_r66451` stores the DRM panel, DSI device, reset GPIO, and two supplies (`vddio`, `vdd`). `visionox_r66451_on()` sends vendor page/register setup, TE enable, and address-window commands. `visionox_r66451_prepare()` enables supplies, resets, runs init, and enables DSI compression mode. `visionox_r66451_enable()` packs DSC PPS using `drm_dsc_pps_payload_pack()`, sends it via `mipi_dsi_picture_parameter_set_multi()`, exits sleep, waits 120 ms, and turns display on.

Panel ops include prepare, unprepare, enable, disable, and get_modes. Backlight update uses 16-bit brightness with max 4095.

## Control Flow
Probe allocates the panel and a managed `drm_dsc_config`, fills DSC version 1.2, slice dimensions, two slices, 8 bpc, 8 bpp, and block prediction, assigns it to `dsi->dsc`, gets regulators and reset GPIO, configures four RGB888 lanes with LPM/non-continuous clock, creates a raw backlight, adds the panel, and attaches to DSI. Prepare powers and initializes vendor registers, then enables compression mode. Enable requires `dsi->dsc`, sends PPS, exits sleep, and turns display on. Disable sends display-off and sleep-in. Unprepare clears LPM, asserts reset, and disables regulators.

## State And Persistence
State includes the DSI DSC config pointer, regulator handles, and reset GPIO. No persistent storage is used. The panel initialization and DSC PPS are replayed during lifecycle transitions.

## Dependencies And Integration Points
The driver integrates with DRM panel, MIPI DSI, DRM DSC helpers, PPS payload packing, regulator bulk APIs, GPIO, backlight core, and fixed-mode helper. Compatible is `visionox,r66451`.

## Risks
DSC configuration is hard-coded and must match the DSI host and panel; a mismatch can produce no image despite successful attach. `get_modes()` uses `drm_connector_helper_get_modes_fixed()` and then returns 1, relying on helper success without checking return. Mode physical dimensions are zero. `visionox_r66451_off()` only clears LPM; actual display-off/sleep is in disable, so lifecycle ordering matters. Backlight brightness maximum is 4095 but DCS helper takes `u16`, so userspace scale must be correct.

## Test Signals
Validate DSC host support and PPS payload transmission, compression mode enabling, fixed mode timing, backlight range, regulator/reset sequencing, and full prepare/enable/disable/unprepare ordering. Hardware tests should include DSC visual integrity and failure behavior when `dsi->dsc` is missing.
