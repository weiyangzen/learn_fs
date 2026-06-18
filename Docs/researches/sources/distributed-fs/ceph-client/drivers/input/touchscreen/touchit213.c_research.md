<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchit213.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchit213.c

## Purpose
`touchit213.c` is a serio RS232 input driver for the Sahara TouchIT-213 serial touchscreen protocol. It decodes five-byte packets into 11-bit X/Y coordinates plus touch state and registers a simple absolute single-touch input device.

## Important APIs, Types, And Functions
`struct touchit213` stores input device, serio port, current packet index, an unused checksum byte, five-byte packet buffer, and physical path. `touchit213_interrupt()` is the byte-by-byte parser. `touchit213_connect()` allocates state and input, sets BUS_RS232 IDs, configures ABS_X/ABS_Y ranges `0..0x07ff`, opens the serio port, and registers input. `touchit213_disconnect()` unregisters input, closes serio, clears driver data, and frees state.

## Control Flow
The serio core matches `SERIO_RS232` with protocol `SERIO_TOUCHIT213`. Incoming byte 0 must have the status-byte pattern `0x80` ignoring the touch bit; otherwise the parser resets to index zero. On the fifth byte, it combines byte pairs as `(msb << 7) | lsb`, reports X, Y, `BTN_TOUCH` from the low bit of byte 0, syncs, and resets the packet index.

## State And Persistence
Only the in-progress packet buffer and index are retained. No calibration, sysfs, firmware, or PM state exists. Input device lifetime is tied to serio connection lifetime.

## Dependencies And Integration Points
The driver integrates solely with the serio bus and input core. It uses the serio protocol ID to bind to line-discipline-created devices and reports BUS_RS232 identity.

## Risks
There is no checksum despite the `csum` member. A lost byte can desynchronize until a new valid status byte appears. The comments mention Touchright in the connect description, inherited from the older driver. Axis orientation/calibration is left to userspace.

## Test Signals
Feed valid and invalid five-byte sequences through serio, verify resync on bad first byte, confirm press and release packets, check 11-bit coordinate limits, and test connect/disconnect cleanup with input users open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchit213.c -->
