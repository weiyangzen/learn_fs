# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-dsi.c

## Purpose

This is the MIPI DSI transport driver for ILI9806E panels using the shared core. It supports Densitron DMT028VGHMCMI-1D and Ortustech COM35H3P70ULC panels, each with a descriptor-provided fixed mode and initialization sequence.

## Important APIs, Types, And Functions

`struct ili9806e_dsi_panel_desc` describes a mode, DSI flags, pixel format, lane count, and optional init sequence. `struct ili9806e_dsi_panel` stores the DSI device, descriptor, and orientation.

`ili9806e_dsi_on()` sends the optional init sequence, exits sleep, waits 120 ms, and turns display on. `ili9806e_dsi_off()` sends display-off and sleep-in. Panel funcs call shared power helpers and use `ili9806e_get_transport()` to recover DSI state. `ili9806e_dsi_probe()` configures the DSI bus, reads orientation, calls the shared core probe, and attaches DSI.

## Control Flow

Probe allocates DSI transport state, gets match data, stores DSI drvdata, applies descriptor DSI flags/format/lanes, reads panel orientation, invokes `ili9806e_probe()` with DSI connector funcs, then attaches the DSI device. Prepare powers on through the core, runs the init sequence, exits sleep, and sets display on. Unprepare sends off/sleep commands, powers off, and returns power-off status.

## State And Persistence

No state is persisted. Runtime state is descriptor match data, orientation, DSI device pointer, and core-owned regulators/reset/backlight. The init sequences program volatile controller pages.

## Dependencies And Integration Points

This file depends on the ILI9806E core header, DRM panel/probe helper, MIPI DSI helpers, OF/device match data, and panel orientation. It integrates with the core by passing transport state and with device tree through `densitron,dmt028vghmcmi-1d` and `ortustech,com35h3p70ulc`.

## Risks

The shared core overwrites device drvdata with its own core state after this file sets DSI drvdata, so remove paths avoid using `mipi_dsi_get_drvdata()` and call the core directly. This is intentional but fragile if future code expects DSI drvdata to be the transport. Init sequences are large page-based register tables and are not validated beyond DSI accumulated error. `mipi_dsi_detach()` return is ignored in remove.

## Test Signals

Check orientation parsing, fixed mode reporting, successful core probe and DSI attach, correct lane/format/mode flags per compatible, visible display after init/sleep-out/display-on, DT backlight binding through the core, and clean DSI detach plus panel removal.
