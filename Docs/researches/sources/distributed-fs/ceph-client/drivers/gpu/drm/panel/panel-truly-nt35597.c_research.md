# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-truly-nt35597.c

## Purpose
This driver supports a dual-DSI Truly NT35597 2K panel, including Qualcomm SDM845 MTP configuration. It registers and attaches a secondary DSI device from the graph, drives both DSI links in parallel for commands, sequences regulators with load votes, controls reset/mode GPIOs, and exposes a fixed 1440x2560 mode.

## Important APIs, Types, And Functions
`struct cmd_set` stores up to four command bytes and size. `struct nt35597_config` describes dimensions, panel name, on-command list, command count, and display mode. `struct truly_nt35597` holds device, DRM panel, three supplies (`vdda`, `vdispp`, `vdispn`), reset/mode GPIOs, optional backlight pointer, two DSI devices, and config.

`truly_dcs_write()` and `truly_dcs_write_buf()` broadcast commands to both DSI links. Power sequencing is in `truly_35597_power_on()` and `truly_nt35597_power_off()`. Panel ops are disable, unprepare, prepare, enable, and get_modes.

## Control Flow
Probe allocates state, gets match config, resolves the remote graph endpoint for the second DSI host, registers a second DSI device, stores both links, adds the panel resources, then configures and attaches both DSI devices. Panel add gets regulators, reset and mode GPIOs, forces dual-port mode via mode GPIO low, initializes and adds the panel. Prepare powers on regulators with enable loads, performs reset toggling, enables LPM on both DSI links, broadcasts the config command list, exits sleep, waits 120 ms, sets display-on, and waits another 120 ms. Unprepare clears DSI mode flags, broadcasts display-off and sleep-in, then powers off and reduces regulator loads.

## State And Persistence
State includes both DSI device pointers, config pointer, GPIO handles, and regulator load state. There is no persistent storage. The command list is static and replayed at each prepare.

## Dependencies And Integration Points
The driver integrates with DRM panel, MIPI DSI, OF graph, secondary DSI device registration, regulators with load setting, GPIOs, optional backlight core, and DSI mode flags. It requires the device tree graph to expose a second DSI host.

## Risks
The dual-DSI attach path has complex cleanup: if attaching the second link fails, already-attached first-link detach is not explicit before panel removal and secondary unregister. `truly_dcs_write()` logs failures but continues and returns the last `ret`, which can mask an earlier DSI failure if a later link succeeds. Backlight pointer is never initialized in this file, so enable/disable backlight calls are currently no-ops unless assigned externally. The vendor command table is large and opaque.

## Test Signals
Test graph resolution and probe deferral for missing second DSI host, secondary device registration/unregistration, both-link command failures, regulator load transitions, reset/mode GPIO polarity, fixed 1440x2560 mode, and attach-failure cleanup. Hardware testing must confirm both DSI links are active and synchronized.
