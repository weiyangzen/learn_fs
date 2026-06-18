# sources/distributed-fs/ceph-client/drivers/input/mouse/maplemouse.c

`maplemouse.c` is the Sega Dreamcast Maple bus mouse driver. It binds Maple devices advertising `MAPLE_FUNC_MOUSE`, starts condition polling while the input device is open, and reports relative X/Y, wheel, and three buttons.

`probe_maple_mouse()` allocates `struct dc_mouse` and `input_dev`, sets capability bitmaps, registers input, and stores Maple driver data. `dc_mouse_open()` and `dc_mouse_close()` enable/disable `maple_getcond_callback()`. `dc_mouse_callback()` decodes response buffer fields at fixed offsets, subtracts 512 from 16-bit relative axes, reports buttons and wheel, and syncs input. Removal clears callbacks, unregisters input, and frees state.

State is per-device input/Maple pointers and active polling only while opened. Dependencies are Maple bus APIs and input. Risks are fixed response-layout assumptions, direct unaligned 16-bit casts, and unusual button bit mapping. Test signals include open/close polling, response decoding, wheel/button mapping, and safe remove/unplug cleanup.
