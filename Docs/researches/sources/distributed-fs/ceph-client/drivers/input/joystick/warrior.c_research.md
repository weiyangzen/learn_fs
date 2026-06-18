# sources/distributed-fs/ceph-client/drivers/input/joystick/warrior.c

Purpose: supports the Logitech WingMan Warrior RS-232 joystick, including buttons, XY axes, throttle, hat, and spinner dial.

Important APIs/types/functions: `struct warrior` tracks input device, current packet index, expected packet length, data buffer, and phys path. `warrior_lengths` maps packet type to length. `warrior_interrupt` frames packets. `warrior_process_packet` decodes packet classes. Connect/disconnect provide serio lifecycle.

Control flow: bytes with the high bit set start a new packet and determine expected length from bits 4-6. A partially collected packet is processed before resync. When the expected length is reached, decode reports one of three supported packet classes: button data, XY-axis data, or throttle/hat/spinner data. The spinner uses `REL_DIAL`; other controls use ABS/KEY events. Connect sets `EV_KEY`, `EV_REL`, and `EV_ABS` capabilities and registers the input device.

State and persistence: only packet framing state persists across interrupts. No calibration or hardware settings are stored.

Dependencies and integration: uses `SERIO_WARRIOR`, Linux input, and standard serio module registration. It exposes `BUS_RS232`.

Risks: packet type lengths are table-driven and unknown types get zero length. There is no checksum. Processing a partial packet on a new high-bit byte can report stale/incomplete data if framing is noisy, though packet class checks limit some effects. Relative dial interpretation depends on exact signed bit packing.

Test signals: inject packet classes 1, 3, and 5, verify high-bit resync, test button/axis/hat/dial events, and validate no events for zero-length or unsupported packet types.
