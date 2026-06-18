# sources/distributed-fs/ceph-client/drivers/input/touchscreen/fujitsu_ts.c

Purpose: `fujitsu_ts.c` is a serio driver for Fujitsu RS-232 serial touchscreens. It decodes five-byte packets and reports single-touch X/Y plus `BTN_TOUCH`.

Important APIs, types, and functions: `struct fujitsu` contains the input device, serio port, packet index, five-byte buffer, and physical path. `fujitsu_interrupt()` implements packet synchronization and decoding. `fujitsu_connect()`/`fujitsu_disconnect()` allocate, register, and tear down the serio/input device pair.

Control flow: the serio ID table matches `SERIO_RS232` with protocol `SERIO_FUJITSU`. Connect allocates state/input, sets BUS_RS232 IDs and 0..4096 ABS ranges, opens the serio port, and registers input. In the interrupt parser, byte 0 must have high nibble `0x80`; later bytes must not have bit 7 set. Once five bytes arrive, X and Y are decoded from two 7-bit bytes each, touch is reported as true unless the low two status bits equal `2`, the event is synced, and the packet index resets.

State and persistence: only the current packet buffer/index and registered input state exist. There are no hardware commands, persistent settings, or PM hooks.

Dependencies and integration points: it depends on serio, input single-touch APIs, and external serial attachment via the Fujitsu protocol ID.

Risks: there is no checksum, so valid-looking corrupted packets can be reported. The first status byte contains calibration/correction/button information, but only the low two bits are used for touch state. Mid-frame bytes with bit 7 set reset the parser and drop the byte rather than treating it as a new start byte.

Test signals: feed valid five-byte packets, garbage before start, high-bit payload resync cases, touch status values, coordinate max ranges, connect unwind paths, and disconnect lifetime handling.
