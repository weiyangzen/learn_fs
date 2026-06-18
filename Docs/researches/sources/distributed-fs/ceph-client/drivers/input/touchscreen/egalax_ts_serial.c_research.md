# sources/distributed-fs/ceph-client/drivers/input/touchscreen/egalax_ts_serial.c

Purpose: `egalax_ts_serial.c` is a serio driver for EETI eGalaxTouch serial touchscreens. It decodes five- or six-byte packets and reports single-touch absolute coordinates plus `BTN_TOUCH`.

Important APIs, types, and functions: `struct egalax` stores input, serio, packet index, six-byte buffer, and physical path. `egalax_interrupt()` accumulates bytes, validates the first byte start bit, chooses packet length based on the pressure bit, and calls `egalax_process_data()`. `egalax_process_data()` derives coordinate resolution from header bits, masks high coordinate bits, combines them with 7-bit low bytes, shifts to the declared 0..0x4000 range, reports touch and X/Y, and syncs. Connect/disconnect implement the usual serio lifecycle.

Control flow: the driver matches `SERIO_RS232` plus `SERIO_EGALAX`. Connect allocates state/input, sets EV_KEY/EV_ABS capabilities and 0..0x4000 ranges, opens serio, and registers input. Runtime interrupts parse frames; malformed start bytes reset the packet index.

State and persistence: only packet assembly state is held. There is no PM, configuration, pressure reporting, or persistence.

Dependencies and integration points: it depends on serio, input single-touch APIs, and external attachment of an eGalax protocol serio port.

Risks: packets with the pressure bit are accepted as six bytes but pressure data is ignored. There is no checksum. If a new start byte appears mid-frame with bit 7 set, it is stored as payload until the length completes rather than resynchronizing immediately.

Test signals: feed 5-byte and 6-byte frames with different resolution bits, verify coordinate scaling and touch bit, validate malformed start reset, connect failure unwinds, and disconnect cleanup.
