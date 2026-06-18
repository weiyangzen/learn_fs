## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-motorola-mot.c

Purpose: This is a DRM MIPI-DSI panel driver for a Motorola MOT 540x960 panel. It sequences `vddio`/`vdd` supplies, reset GPIO, a long vendor ES2 initialization sequence with gamma tables, fixed mode reporting, and external backlight binding.

Important APIs, types, and functions: `mot_panel_supplies[]` defines the two rails. `struct mot_panel` stores DRM panel, DSI device, reset GPIO, and regulator bulk array. `mot_panel_reset()` asserts/deasserts reset with long delays. `mot_es2()` writes manufacturer/vendor command sequences, exits sleep early, waits, programs gamma for R/G/B/W, sets display control and tear-on. `mot_panel_prepare()` enables regulators, resets, unlocks command pages, runs `mot_es2()`, and sets display on. `mot_panel_disable()` sends display-off and sleep-in. `mot_panel_unprepare()` asserts reset and disables supplies. `mot_panel_get_modes()` exposes the fixed mode.

Control flow: Probe uses bulk regulators, optional reset GPIO, DSI two-lane RGB888 LPM mode, external backlight, panel add, and devm DSI attach. Prepare performs the full vendor init and display-on. There is no separate `enable` hook; display-on is in prepare. Disable sends sleep commands; unprepare handles reset and power removal.

State and persistence: Software state is resource-only. Hardware state includes command-page unlocks, gamma tables, CABC/display control, tear-on, sleep/display state, and reset/power state. The panel runs over two DSI lanes and starts in LPM; no mode flag mutation is done later.

Dependencies and integration points: The driver depends on DRM fixed-mode helper, MIPI-DSI multi-context helpers, regulator bulk APIs, GPIO, backlight lookup, and OF compatible `motorola,mot-panel`.

Risks: The ES2 sequence exits sleep before most gamma/power commands, so ordering must not be "cleaned up" casually. `mot_panel_prepare()` returns accumulated DSI errors but does not power off on failure after regulators are enabled. The reset GPIO is optional; if absent, the reset helper silently does nothing, which may not work on boards needing reset. Panel identity is broad (`motorola,mot-panel`) with no revision data beyond the ES2 sequence.

Test signals: Confirm fixed 540x960 mode with 51x91 mm size, successful two-lane DSI attach, backlight binding, correct reset timing, no accumulated DSI errors through ES2 init, display-on after prepare, sleep entry on disable, and regulator disable on unprepare. Fault testing should inspect power cleanup after failed DSI writes.
