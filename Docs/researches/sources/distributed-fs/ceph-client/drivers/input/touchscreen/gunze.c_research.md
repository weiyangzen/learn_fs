# sources/distributed-fs/ceph-client/drivers/input/touchscreen/gunze.c

## Purpose
`gunze.c` is a serio driver for Gunze AHL-51S RS232 touchscreens. It receives ASCII packets from the serio line, parses X/Y/touch state, and exposes a simple absolute-position input device.

## Important APIs, types, and functions
- `struct gunze` stores the input device, serio port, packet index, 10-byte packet buffer, and physical path string.
- `gunze_interrupt()` collects bytes until carriage return, then processes the packet and resets the buffer index.
- `gunze_process_packet()` validates packet length, comma delimiter, and leading `T` or `R`, then reports `ABS_X`, inverted `ABS_Y`, and `BTN_TOUCH`.
- `gunze_connect()` allocates state/input, opens the serio port, and registers the input device.
- `gunze_disconnect()` unregisters input, closes serio, clears driver data, and frees state.

## Control flow
The serio core matches `SERIO_RS232` with protocol `SERIO_GUNZE`. On connect, the driver initializes an input device with fixed X/Y ranges 24..1000. Each incoming byte advances packet state; `\r` terminates a packet. Valid packets are converted with `simple_strtoul()` from fixed decimal fields.

## State and persistence
State is limited to the in-progress packet buffer and input device lifetime. There is no hardware configuration or persistent storage.

## Dependencies and integration points
The driver integrates with the serio subsystem and input core, typically through userspace `inputattach` selecting the Gunze protocol.

## Risks
- Packet parsing assumes a fixed 10-byte ASCII layout and uses weak validation; malformed numeric fields can be accepted as zero or partial values.
- Bad packets log with `printk()` and raw packet contents, which can be noisy on an unsynchronized serial line.
- The Y coordinate is hard-coded as `1024 - value`; panel variants with different scaling need userspace calibration.

## Test signals
- Use serio/inputattach with valid `Txxxxx,yyyy` and release packets.
- Fuzz packet lengths, delimiter placement, CR resynchronization, and nonnumeric fields.
- Confirm disconnect during active serial input does not use freed state.
