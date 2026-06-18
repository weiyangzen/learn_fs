# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9882t.c

## Purpose

This DRM panel driver supports panels based on Ilitek ILI9882T-class controllers, plus the Tianma `tl121bvms07-00` path using an IL79900A command-page convention and DSC. Each panel is selected by OF match data and described by static mode, physical size, bpc, DSI format, lane count, mode flags, optional DSC configuration, and an init callback.

## Important APIs, Types, And Functions

- `struct panel_desc` is the per-compatible contract for mode, DSC, dimensions, bpc, DSI settings, init callback, and lane count.
- `struct ili9882t` holds the `drm_panel`, DSI device, descriptor, orientation, four regulators, enable GPIO, and copied DSC config.
- `starry_ili9882t_init()` sends the large ILI9882T vendor init script and standard display-on sequence.
- `tianma_il79900a_init()` writes IL79900A registers, packs/sends DSC PPS, enables DSI compression mode, exits sleep, and turns display on.
- `ili9882t_prepare()` sequences regulators, establishes LP11 with a DSI NOP, toggles enable/reset, and invokes descriptor init.
- `ili9882t_disable()` sends display off and sleep mode; `ili9882t_unprepare()` drops GPIO and regulators.
- `ili9882t_probe()` configures DSI, installs `dsi->dsc` when needed, registers the panel, and attaches.

## Control Flow

Probe selects either `starry,ili9882t` for a 1200x1920 4-lane RGB888 panel or `tianma,tl121bvms07-00` for a 1600x2560 3-lane RGB888 panel using DSC 1.2. Prepare enables `pp3300`, `pp1800`, `avdd`, and `avee`, sends LP11 NOP, toggles the enable GPIO sequence, then runs the selected init callback. Disable performs DCS display-off/sleep; unprepare powers down. `get_modes()` exposes one preferred descriptor mode and `get_orientation()` returns DT orientation.

## State And Persistence

No persistent storage is used. The driver caches descriptor-derived state and a copied DSC configuration in memory. Panel register and DSC PPS state are volatile and rebuilt on prepare.

## Dependencies And Integration Points

The file depends on DRM panel/mode APIs, MIPI DSI helpers, regulator and GPIO frameworks, OF orientation parsing, and DRM DSC helpers. DSC integration is a key DSI-host contract because `dsi->dsc` is set before attach for the Tianma panel.

## Risks

Power sequencing is delicate. The prepare error path can leave `pp3300` enabled if `pp1800` or later steps fail. `ili9882t_disable()` uses the ILI9882T page-switch command even for the IL79900A-compatible panel. DSC parameters, lane count, PPS payload, and mode timing must match the panel and host exactly.

## Test Signals

Check compile coverage with DRM DSC, regulator/GPIO sequencing, DSI attach with `dsi->dsc` populated for Tianma, one preferred mode, orientation, repeated blank/unblank without leaked rails, and visual validation for DSC artifacts or blank display.
