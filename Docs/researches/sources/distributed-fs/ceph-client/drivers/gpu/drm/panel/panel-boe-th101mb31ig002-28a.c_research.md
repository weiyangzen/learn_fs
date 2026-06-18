# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-boe-th101mb31ig002-28a.c

Purpose: Descriptor-driven MIPI DSI panel driver for BOE TH101MB31IG002-28A and Starry ER88577 800x1280 LCD panels.

Important APIs/types/functions: `struct panel_desc` captures mode, DSI flags, init callback, lanes, LP11/reset delays, and power-off delays. `struct boe_th101mb31ig002` stores panel, DSI, descriptor, power regulator, enable/reset GPIOs, and orientation. Provides reset, two init-command functions, disable/unprepare/prepare, get_modes/get_orientation, descriptors, OF match, and DSI probe/remove.

Control flow: Probe selects descriptor, configures DSI, gets `power`, `enable`, optional `reset`, reads panel orientation from DT, attaches OF backlight, registers panel, and attaches to DSI. Prepare enables power, optionally enters LP11 before reset, waits descriptor-defined delays, enables panel, resets, and calls the descriptor init sequence. Disable waits optional backlight delay, sends display-off, sleep-in, and optional reset delay. Unprepare drives reset/enable low and disables power with optional off delay. Modes are reported through the fixed-mode helper and orientation is exposed through both connector and panel funcs.

State and persistence: State is per DSI device. Descriptor data is static and controls timing/power behavior for each compatible.

Dependencies and integration: Depends on DRM MIPI DSI, regulator, GPIO, OF device match data, OF panel orientation, DRM probe helper, and DRM panel backlight integration.

Risks: Optional reset GPIO is used by `boe_th101mb31ig002_reset`; platforms without reset must be verified against gpiod optional semantics. Prepare does not undo regulator/enable on init failure. Descriptor timing mistakes can break one compatible while the other works.

Test signals: Both compatibles, orientation property handling, LP11-before-reset sequence for Starry, power failure cleanup review, fixed-mode enumeration, backlight delay behavior, and DSI command error propagation.
