## sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-lxd-m9189a.c

Purpose: This driver supports the LXD M9189A 1024x600 MIPI-DSI panel using EK79007AD3 manufacturer commands. It handles power, reset, standby GPIOs, gamma setup, sleep/display state, fixed-mode reporting, and external backlight binding.

Important APIs, types, and functions: Manufacturer command macros define gamma registers and panel control. `struct m9189_panel` stores the DRM panel, DSI device, `power` regulator, reset GPIO, and standby GPIO. `m9189_reset()` performs a low/high/low reset sequence. `m9189_on()` sets LPM, writes gamma values, configures four-lane panel control, exits sleep, and turns display on. `m9189_disable()` clears LPM, enters sleep, and asserts standby. `m9189_prepare()` enables power, deasserts standby, resets, and runs `m9189_on()`. `m9189_unprepare()` asserts standby/reset and disables the regulator. Probe uses manual `devm_kzalloc()` plus `drm_panel_init()` rather than `devm_drm_panel_alloc()`.

Control flow: Probe requests mandatory regulator/reset/standby resources, fixes DSI to four lanes RGB888 video burst, initializes the panel with `prepare_prev_first = true`, binds an external backlight, adds the panel, and attaches to DSI. Prepare powers and resets, then executes the DSI init. Disable and unprepare are separate; disable performs DCS sleep-in while unprepare removes power and asserts control GPIOs.

State and persistence: Runtime software state is the DSI device and resources. The code mutates `dsi->mode_flags` in enable/disable paths to add or remove LPM, leaving bus mode dependent on last lifecycle stage. Hardware state includes gamma values, four-lane configuration, sleep/display state, standby GPIO, and reset/power state.

Dependencies and integration points: The driver depends on DRM panel, DRM probe fixed-mode helper, MIPI-DSI multi-context helpers, regulator/GPIO APIs, OF matching, and `drm_panel_of_backlight()`. Compatible string is `lxd,m9189a`.

Risks: `nt->mode_flags` changes are asymmetric: `m9189_on()` ORs LPM, while `m9189_disable()` clears it, which may interact with host assumptions. `m9189_disable()` enters sleep without an explicit display-off. Probe uses manual allocation but still devm-managed memory; cleanup relies on remove. Reset/standby polarity must match the generated vendor sequence. Error path in prepare asserts reset high and disables supply but does not reassert standby.

Test signals: Validate one fixed 1024x600 mode with 154x86 mm size, successful DSI attach and backlight binding, correct standby/reset waveform, gamma writes without accumulated errors, visible output after prepare, sleep entry on disable, and clean power-off on unprepare.
