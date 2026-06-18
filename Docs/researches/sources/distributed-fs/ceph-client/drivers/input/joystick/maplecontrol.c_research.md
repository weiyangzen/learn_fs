# sources/distributed-fs/ceph-client/drivers/input/joystick/maplecontrol.c

Purpose: Sega Dreamcast Maple bus controller driver. It registers Dreamcast controller input devices and polls condition data through the Maple subsystem.

Important APIs/types/functions: `struct dc_pad` stores input device and Maple device. `dc_pad_callback()` decodes Maple condition response bytes into buttons, hats, triggers, and analog axes. `dc_pad_open()` starts periodic `maple_getcond_callback()` polling at `HZ/20`; `dc_pad_close()` stops it. `probe_maple_controller()` builds input capabilities from `function_data`. `remove_maple_controller()` unregisters input and clears callback state.

Control flow: Maple driver probe allocates pad/input, inspects function data bitfields to set key/ABS capabilities, configures axis ranges, registers input, and stores driver data. Opening input schedules Maple condition callbacks. Each callback decodes response buffer offsets 8..15 and reports events. Removal unregisters input and frees pad state.

State and persistence: Per-controller state includes input and Maple device pointers. Polling is active only while input is open. No persistent storage.

Dependencies and integration points: Dreamcast Maple bus, input core, Maple condition polling, and `MAPLE_FUNC_CONTROLLER`.

Risks: Callback assumes response buffer layout and sufficient length. Hat axis ranges are configured with min 1 and max -1 in this snapshot, which is unusual and should be tested. Capabilities depend on device-advertised function bits; bad firmware data may hide controls.

Test signals: Dreamcast controller probe; open/close callback scheduling; response buffer with each button/axis bit; function_data capability filtering; remove while callback is active.
