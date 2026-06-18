# sources/distributed-fs/ceph-client/drivers/input/mouse/lifebook.c

`lifebook.c` supports DMI-identified Fujitsu Lifebook and Panasonic PS/2 touchscreen/touchpad devices. It uses DMI-only detection to avoid disturbing unrelated mice and can operate in 3-byte or 6-byte absolute protocols.

`lifebook_module_init()` sets global DMI state, including optional serio restriction and 6-byte protocol selection. `lifebook_detect()` gates psmouse protocol selection. `lifebook_init()` enters absolute mode, clears generic relative capabilities on the primary device, configures absolute axes, optionally creates a second relative input device, and installs `lifebook_process_byte()`. The packet handler distinguishes relative packets from absolute packets, validates 6-byte packet structure, reports coordinates/touch on the main device, and reports standard motion/buttons on the secondary device.

State includes module-lifetime DMI flags and per-device optional relative input state. Dependencies are psmouse, libps2, DMI, and input. Risks are broad DMI matching, expected-failing absolute-mode command side effects, `pktsize` remaining 3 for a 6-byte stream, and false positives hijacking normal mice. Test signals include DMI/serio matching, 1024 vs 4096 ranges, secondary device lifecycle, packet validation, reconnect absolute mode, and fallback to relative mode on setup failure.
