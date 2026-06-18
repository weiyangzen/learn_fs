# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-orisetech-otm8009a.c

Purpose: DRM MIPI-DSI driver for Orise Tech OTM8009A panels, providing two 480x800 modes and a DSI-command-based raw backlight implementation.

Important APIs, types, and functions: `struct otm8009a` stores device, DRM panel, backlight device, reset GPIO, regulator, and `prepared` flag. Large MCS command macros encode address-shifted manufacturer commands. Core functions are `otm8009a_probe()`, `otm8009a_init_sequence()`, `otm8009a_prepare()`, `otm8009a_enable()`, `otm8009a_disable()`, `otm8009a_unprepare()`, `otm8009a_get_modes()`, and `otm8009a_backlight_update_status()`.

Control flow: probe allocates the panel, gets optional reset GPIO and `power` regulator, configures two-lane RGB888 DSI video burst with LPM and non-continuous clock, registers an internal raw backlight, adds the panel, and attaches. Prepare enables power, toggles reset, sends a long manufacturer initialization sequence, exits sleep, sets address windows/pixel format/CABC, turns display on, starts memory write, and marks `prepared`. Enable turns the internal backlight on. Disable disables the backlight, then sends display-off and sleep-mode. Unprepare asserts reset, disables power, and clears `prepared`.

State and persistence: no durable state. The `prepared` flag prevents DSI brightness writes before panel initialization. Backlight properties hold volatile brightness/power state.

Dependencies and integration points: DRM panel, MIPI DSI, regulator, optional GPIO, backlight core, and OF match `orisetech,otm8009a`.

Risks and test signals: if `otm8009a_init_sequence()` fails, prepare returns without disabling the regulator, so error rollback is incomplete. `get_modes()` copies physical size from the last duplicated mode pointer after the loop, which is safe only because both mode entries use the same size. Test command failure paths, backlight before prepare, mode ordering/preferred flag, regulator rollback, reset-optional systems, and suspend/resume.
