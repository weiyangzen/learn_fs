# sources/distributed-fs/ceph-client/drivers/input/touchscreen/inexio.c

## Purpose
`inexio.c` is a serio driver for iNexio RS232 touchscreens. It decodes 5-byte binary packets into absolute X/Y coordinates and `BTN_TOUCH` state for the Linux input subsystem.

## Important APIs, types, and functions
- Packet macros define begin bit, touch bit, 5-byte packet length, coordinate ranges, and coordinate extraction.
- `struct inexio` stores input device, serio port, packet index, 16-byte buffer, and physical path string.
- `inexio_interrupt()` stores incoming bytes, starts processing only when byte 0 has the response begin bit, and logs unsynchronized bytes.
- `inexio_process_data()` reports X/Y/touch when five bytes have been accumulated and resets the index.
- `inexio_connect()` and `inexio_disconnect()` manage serio and input lifetimes.

## Control flow
The serio core binds `SERIO_RS232` protocol `SERIO_INEXIO`. Connect allocates state/input, sets fixed 0..0x3fff axes, opens the serio port, and registers input. Each byte is appended to the packet buffer; after a valid begin byte and five total bytes, the driver reports the decoded coordinates and touch bit.

## State and persistence
State is limited to packet assembly and the input device. There is no hardware configuration, firmware, or persistent calibration.

## Dependencies and integration points
The driver integrates with serio and input, normally through userspace protocol attachment for serial touchscreens.

## Risks
- The interrupt path does not bound-check `idx` against `INEXIO_MAX_LENGTH` before storing; persistent unsynchronized data after a begin byte could overrun if packet completion logic is disrupted.
- There is no checksum; serial noise after a begin byte becomes input data.
- Coordinate ranges are fixed and may require userspace calibration for a given panel.
- Logging uses raw `printk()` style and can be noisy on bad serial data.

## Test signals
- Feed valid 5-byte frames, release frames, unsynchronized bytes, and partial frames through serio.
- Test repeated invalid streams for index bounds and resynchronization.
- Verify connect/disconnect while data is arriving.
