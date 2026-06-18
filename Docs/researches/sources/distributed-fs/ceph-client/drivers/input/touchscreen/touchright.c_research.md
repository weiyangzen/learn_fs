<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchright.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchright.c

## Purpose
`touchright.c` is a legacy serio RS232 driver for Touchright serial touchscreens. It decodes fixed five-byte packets into 9-bit X/Y coordinates and reports absolute single-touch events through the input subsystem.

## Important APIs, Types, And Functions
`struct tr` stores input device, serio port, current packet index, five-byte packet buffer, and physical path. `tr_interrupt()` parses incoming bytes. `tr_connect()` allocates state/input, assigns BUS_RS232 IDs with vendor `SERIO_TOUCHRIGHT`, sets ABS_X/ABS_Y ranges `0..0x1ff`, opens the serio port, and registers the input device. `tr_disconnect()` unregisters input, closes serio, clears driver data, and frees memory.

## Control Flow
The serio driver binds to `SERIO_RS232` protocol `SERIO_TOUCHRIGHT`. For each byte, the parser stores it in `data[idx]`. If the first byte has the required status pattern `0x40` ignoring the touch bit, the index advances. Once five bytes are present, X is `(data[1] << 5) | (data[2] >> 1)`, Y is `(data[3] << 5) | (data[4] >> 1)`, touch state is bit 0 of byte 0, and the input frame is synced.

## State And Persistence
State is limited to packet assembly and input lifetime. The driver stores no calibration or persistent settings and has no PM hooks.

## Dependencies And Integration Points
It uses the serio bus, input core, module serio registration, and protocol IDs. It assumes userspace handles calibration/rotation if raw coordinate orientation differs from display orientation.

## Risks
If `data[0]` is invalid, `idx` does not advance but the current byte remains in slot zero, so resynchronization depends on a future byte matching the status pattern. There is no checksum or timeout-based packet reset. Coordinates are reported raw.

## Test Signals
Test valid press/release packet decoding, invalid leading-byte recovery, max/min coordinate values, serio open failure cleanup, and disconnect while the input device is referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchright.c -->
