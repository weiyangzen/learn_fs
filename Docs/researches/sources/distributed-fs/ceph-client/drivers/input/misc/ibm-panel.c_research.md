<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ibm-panel.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/ibm-panel.c

## Purpose
`ibm-panel.c` implements an I2C slave input driver for an IBM operation panel. It receives fixed-length panel commands over I2C slave callbacks, validates them, and reports one of three configurable button keycodes.

## Important APIs, Types, and Functions
`struct ibm_panel` stores the current receive index, 11-byte command buffer, three keycodes, a spinlock protecting receive state, and input device. `ibm_panel_i2c_slave_cb()` handles slave events and accumulates writes. `ibm_panel_process_command()` validates command header and checksum, extracts the button number from byte 2, and reports key press/release based on bit 7. `ibm_panel_calculate_checksum()` implements the panel checksum over the command bytes.

## Control Flow
Probe allocates state and input, reads optional `linux,keycodes` array or defaults to `BTN_NORTH`, `BTN_SOUTH`, and `BTN_SELECT`, registers input capabilities, registers the input device, stores client data, and registers as an I2C slave. During an I2C write, `WRITE_REQUESTED` resets the index, `WRITE_RECEIVED` stores bytes up to the fixed command size, and `STOP` processes only exactly 11-byte commands. Read requests return `0xff`. Remove unregisters the slave callback.

## State and Persistence Behavior
Partial I2C command state lives in memory under a spinlock and is reset on stop or new write. Key states live in the input core. No data persists across driver lifetime.

## Dependencies and Integration Points
The driver depends on I2C slave support, input, OF compatible `ibm,op-panel`, firmware keycode property parsing, and spinlock guards.

## Risks and Test Signals
Risks include command rejection caused by any size mismatch, checksum/header assumptions, holding a spinlock while calling `input_report_key()`/`input_sync()`, and only three button slots. Tests should cover valid press/release commands, checksum failures, overlong and short commands, custom keycodes, and slave registration failure after input registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ibm-panel.c -->
