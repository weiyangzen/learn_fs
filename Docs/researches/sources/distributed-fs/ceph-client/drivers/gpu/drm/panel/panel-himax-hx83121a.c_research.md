# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-himax-hx83121a.c

## Purpose

This driver supports Himax HX83121A panels, currently BOE and CSOT PPC357DB1-4 variants used on dual-DSI 1600x2560 panels. It can operate in a normal non-DSC mode or an optional DSC mode selected by the `enable_dsc` module parameter.

## Important APIs, Types, And Functions

`struct himax` contains the DRM panel, up to two DSI devices, descriptor, mutable DSC config, reset GPIO, regulators, and backlight. `struct panel_desc` captures physical size, bpc, DSI lanes/format/flags, DSC config and modes, non-DSC modes, init callbacks, dual-DSI status, and DCS backlight support.

`himax_probe()` handles both primary and secondary DSI host registration. `himax_prepare()` powers supplies, resets, chooses the DSC or non-DSC init callback, optionally packs and sends the DSC picture parameter set, enables compression mode, and enables backlight. `himax_get_modes()` chooses between `dsc_modes` and `modes` based on the module parameter. `himax_create_backlight()` creates a raw DCS brightness backlight.

## Control Flow

Probe allocates the panel, obtains `vddi`, `avdd`, and `avee`, reads reset GPIO, loads descriptor data, copies the DSC configuration, then registers a secondary DSI device from OF graph port 1 when `is_dual_dsi` is true. It creates either a DCS backlight or a DT-provided backlight, adds the panel, applies descriptor DSI bus settings to one or both links, assigns `dsi->dsc` only when DSC is enabled, and attaches each DSI device with devm-managed attach.

Prepare enables regulators, toggles reset, sends the selected BOE or CSOT init sequence, then sends PPS and enables compression if `enable_dsc` is true. Unprepare sends sleep-in on the primary command DSI (`dsi[1]` for dual DSI), asserts reset, and disables regulators.

## State And Persistence

The only cross-call state is in memory: the selected descriptor, DSI pointers, copied DSC config, module parameter value, reset GPIO, regulators, and backlight. The module parameter is global to the module and affects exposed modes, init sequence, DSI DSC pointer assignment, and runtime compression setup. There is no persistent storage.

## Dependencies And Integration Points

The driver depends on DRM panel, MIPI DSI, OF graph for the secondary DSI host, DRM DSC helpers, backlight, regulators, and GPIO. It exposes OF matches `boe,ppc357db1-4` and `csot,ppc357db1-4`. Dual-DSI integration requires a valid graph connection for the secondary host. DCS brightness is sent through the command-primary link selected by `to_primary_dsi()`.

## Risks

`enable_dsc` is a module-wide switch, not a per-panel or per-connector setting, so mixed deployments are risky. DSC and non-DSC mode lists differ in refresh-rate support and timing; choosing the wrong path can mismatch host bandwidth, PPS, and panel register state. Dual-DSI attach relies on OF graph correctness and uses DSI1 as command sync, which must match hardware wiring. Backlight enable is called after panel init but errors from DCS brightness mapping are not calibrated, and a TODO notes raw brightness mapping is incomplete.

## Test Signals

Validate both module-parameter paths: non-DSC 60 Hz and DSC modes including 120 Hz/60 Hz. Confirm two DSI devices attach on dual-DSI panels, `dsi->dsc` is populated only in DSC mode, PPS/compression commands succeed, the expected BOE or CSOT sequence is selected from OF match data, and backlight brightness works after prepare and across suspend/resume.
