# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/m5602/m5602_sensor.h

## Purpose
`m5602_sensor.h` defines the common sensor interface used by all ALi M5602 sensor backends. It centralizes private V4L2 control IDs, sensor enum values used by `force_sensor`, register-script instruction types, and the callback vtable.

## Important APIs, Types, And Functions
Private controls are `M5602_V4L2_CID_GREEN_BALANCE` and `M5602_V4L2_CID_NOISE_SUPPRESION`. `enum sensors` assigns force IDs for OV9650, S5K83A, S5K4AA, MT9M111, PO1030, and OV7660. `enum instruction` defines `BRIDGE`, `SENSOR`, and `SENSOR_LONG` script entries. `struct m5602_sensor` contains name, I2C slave ID, register width, and optional lifecycle callbacks.

## Control Flow
No executable logic exists. `m5602_core.c` stores a pointer to one `struct m5602_sensor`, calls `probe()` candidates until one succeeds, then delegates init, control setup, start, stop, and disconnect through this vtable.

## State, Persistence, And Dependencies
The header has no mutable state. It depends on `m5602_bridge.h`, which defines `struct sd`, bridge registers, and the M5602 USB/I2C helper prototypes. The `i2c_regW` field directly controls core sensor read/write validation and protocol construction.

## Integration Points
Every sensor-specific header includes this file and then defines a static descriptor. V4L2 controls in sensor implementations store pointers in `struct sd` and share private control IDs from here.

## Risks
The enum values are user-facing through the `force_sensor` module parameter, so renumbering would break diagnostics and scripts. Callback pointers can be NULL for optional operations, so the core must guard them. `SENSOR_LONG` support is implemented only in some sensor script loops, not in the generic core.

## Test Signals
Compile all sensor backends, verify `force_sensor` values documented by the module match enum values, exercise NULL optional callbacks, and validate one-byte versus two-byte register-width enforcement.
