# sources/distributed-fs/ceph-client/drivers/input/joystick/spaceorb.c

Purpose: implements the SpaceTec SpaceOrb 360 and Avenger RS-232 controller driver, converting proprietary 6DOF motion, button, reset, and error packets into input events.

Important APIs/types/functions: `struct spaceorb` holds an input device, packet index, buffer, and phys string. `spaceorb_process_packet` validates XOR checksum and decodes packets. `spaceorb_interrupt` frames packets using the high bit as start indication. `spaceorb_connect` sets up six axes and six buttons.

Control flow: incoming bytes with bit 7 clear start a new packet; an existing buffered packet is processed before reset. All stored bytes are masked to 7 bits. The decoder rejects short packets and nonzero XOR checksums. Reset packets log device information. `D` packets XOR payload bytes with `"SpaceWare"`, unpack six 10-bit signed axes, report six buttons, and sync. `K` packets report buttons only; `E` packets log mapped device errors.

State and persistence: state is limited to the current receive buffer and index. There is no stored calibration or persistent configuration.

Dependencies and integration: uses the serio and input subsystems with `SERIO_SPACEORB` matching, `BUS_RS232` IDs, ABS_X/Y/Z/RX/RY/RZ axes, and `BTN_TL/TR/Y/X/B/A`.

Risks: malformed checksums and unexpected lengths are ignored without recovery beyond start-bit resynchronization. Axis unpacking is protocol-specific and tightly coupled to exact byte positions. Error reporting only logs device error bits. There is no debounce or rate limiting on valid input events.

Test signals: inject valid and corrupt frames into a serio test path, verify XOR rejection, reset/error log messages, signed axis conversion around the 0x200 sign bit, and button-only versus full data packet behavior.
