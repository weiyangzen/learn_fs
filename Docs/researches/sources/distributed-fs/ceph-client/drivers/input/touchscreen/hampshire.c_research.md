# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hampshire.c

## Purpose
`hampshire.c` is a serio driver for Hampshire 4-byte serial touchscreens. It decodes a compact binary packet format into absolute X/Y and touch state input events.

## Important APIs, types, and functions
- Packet macros decode the touch bit and 12-bit X/Y coordinates from four bytes.
- `struct hampshire` stores input device, serio port, current index, 4-byte packet buffer, and physical path.
- `hampshire_interrupt()` accepts bytes only when the first byte has the begin bit and advances packet parsing.
- `hampshire_process_data()` emits `ABS_X`, `ABS_Y`, and `BTN_TOUCH` when a full packet is collected.
- `hampshire_connect()` and `hampshire_disconnect()` implement serio/input lifetime.

## Control flow
The driver binds to `SERIO_HAMPSHIRE`. Connect allocates and registers an RS232 input device with X/Y ranges 0..0x1000. The interrupt callback stores each byte at the current packet index. If byte 0 has `0x80`, packet assembly continues; otherwise the byte is logged as unsynchronized. At four bytes, coordinates and touch state are reported and the index is reset.

## State and persistence
Only packet assembly state persists between interrupts. The driver does not send commands to the device or persist calibration.

## Dependencies and integration points
Integration is through the serio core and input subsystem, with RS232 protocol selection usually provided by userspace attachment.

## Risks
- Resynchronization is minimal: non-begin bytes at index 0 are ignored, but unexpected bytes after a valid begin byte are trusted.
- Coordinate extraction is macro-heavy and sensitive to bit layout; endian-like mistakes would produce plausible but wrong positions.
- No checksum exists, so serial noise can become input events.

## Test signals
- Feed known 4-byte frames and verify exact coordinate/touch decoding.
- Test loss of sync, partial packets, and reconnect/disconnect behavior.
- Validate min/max ranges against real Hampshire hardware calibration.
