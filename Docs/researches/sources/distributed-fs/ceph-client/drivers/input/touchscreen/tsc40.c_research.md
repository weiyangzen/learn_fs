# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc40.c

## Purpose
`tsc40.c` is a serio/RS232 input driver for TSC-10, TSC-25, and TSC-40 serial touchscreens. It parses fixed five-byte packets and reports single-touch absolute coordinates.

## Important APIs, Types, And Functions
`struct tsc_ser` stores serio/input handles, packet index, five-byte buffer, and physical path. `tsc_interrupt()` is the byte-at-a-time parser and resynchronizer. `tsc_process_data()` decodes 10-bit X/Y coordinates and reports `BTN_TOUCH`. `tsc_connect()` allocates devices, opens serio, and registers input; `tsc_disconnect()` reverses that setup.

## Control Flow
The serio core matches `SERIO_RS232` with protocol `SERIO_TSC40`. Incoming bytes are accumulated from a validated start byte. A start byte with pen-up bit clear emits release immediately. Invalid high bits in coordinate bytes reset the parser. A complete packet emits X/Y/down events.

## State And Persistence
Parser state is just `idx` plus the current data buffer. There is no calibration, persistent configuration, or PM state.

## Dependencies And Integration Points
It depends on the serio bus and input subsystem. It exposes a RS232 input device with 0..0x3ff X/Y axes.

## Risks
The parser reports down for every complete coordinate packet but only reports up from a specific first-byte condition. Noise can cause resynchronization drops. No pressure or debounce filtering is present.

## Test Signals
Test connect/open/register failures, valid packets, pen-up first-byte packet, malformed start and coordinate bytes, stream resynchronization, and disconnect during partial packet reception.
