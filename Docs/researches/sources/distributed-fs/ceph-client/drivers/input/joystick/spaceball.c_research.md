# sources/distributed-fs/ceph-client/drivers/input/joystick/spaceball.c

Purpose: supports SpaceTec SpaceBall 1003/2003/3003/4000 FLX RS-232 controllers through the serio subsystem, decoding six-degree-of-freedom motion and button packets into input events.

Important APIs/types/functions: `struct spaceball` keeps the `input_dev`, packet index, escape state, packet buffer, and physical path. `spaceball_process_packet` decodes packet types. `spaceball_interrupt` assembles carriage-return-terminated packets and handles `^` escaping. `spaceball_connect` and `spaceball_disconnect` bind/unbind serio devices.

Control flow: serio matching accepts `SERIO_RS232` with `SERIO_SPACEBALL`. Connect validates the serio ID, allocates state and input device, configures buttons according to model, sets six axes, opens serio, and registers input. The interrupt handler buffers bytes until `0x0d`, unescapes encoded control bytes, and calls the packet decoder. `D` packets report six signed big-endian axes, `K` and `.` packets report normal or advanced buttons, and error packets are logged.

State and persistence: packet assembly state is transient in `idx`, `escape`, and `data`; no persistent configuration is stored. Device identity comes from serio IDs.

Dependencies and integration: depends on `serio`, Linux input, and `get_unaligned_be16`. It reports `BUS_RS232` devices with SpaceBall vendor/product metadata and standard ABS/BTN codes.

Risks: malformed packet lengths are silently ignored after `input_sync` for recognized paths. Packet buffering truncates after `SPACEBALL_MAX_LENGTH`, so bad framing can drop data until the next CR. Button capability setup varies by ID and could omit capabilities for incorrectly tagged adapters. No checksum is present.

Test signals: exercise with real or emulated SpaceBall serial frames, verify CR and escape decoding, validate six-axis signed ranges with `evtest`, test advanced 4000FLX button packets, and confirm disconnect frees serio/input state.
