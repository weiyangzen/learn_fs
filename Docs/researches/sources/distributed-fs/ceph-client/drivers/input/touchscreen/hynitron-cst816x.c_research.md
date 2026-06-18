# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hynitron-cst816x.c

## Purpose
`hynitron-cst816x.c` is a compact I2C driver for Hynitron CST816x-series single-touch controllers with optional gesture key reporting.

## Important APIs, types, and functions
- `struct cst816x_touch` models the 7-byte touch report: gesture, active state, and big-endian packed X/Y.
- `struct cst816x_priv` stores client, optional reset GPIO, input device, gesture keycodes, and keycode count.
- `cst816x_parse_keycodes()` reads optional `linux,keycodes` into a five-entry array.
- `cst816x_i2c_read_register()` performs command-plus-read I2C transfer.
- `cst816x_gest_idx()` maps supported gesture IDs to keycode indexes.
- `cst816x_process_touch()` reads and decodes 12-bit X/Y.
- `cst816x_register_input()` configures ABS_X/ABS_Y, `BTN_TOUCH`, and optional gesture key capabilities.
- `cst816x_irq_cb()` reads one report and emits coordinates, gesture key state, touch state, and sync.

## Control flow
Probe allocates state, gets optional reset GPIO, performs reset if present, parses optional keycodes, registers the input device, and requests a threaded IRQ. Every IRQ reads from register `0x01`, reports raw coordinates on fixed 0..240 axes, optionally reports the mapped gesture key, reports `BTN_TOUCH`, and syncs.

## State and persistence
State is minimal and devm-managed. There is no power, firmware, or configuration persistence. Gesture key mappings persist only for the input device lifetime.

## Dependencies and integration points
The driver integrates with I2C, GPIO reset, input, optional device properties, OF/I2C matching, and threaded IRQs.

## Risks
- If no valid `linux,keycodes` are provided, `keycodemax` remains zero, but IRQ still indexes `priv->keycode[cst816x_gest_idx()]` for any nonzero gesture. A controller gesture without keycodes can therefore report KEY_RESERVED or uninitialized mappings.
- `cst816x_gest_idx()` maps unsupported gestures to the last index; this requires enough configured keycodes to be meaningful.
- Axis limits are hard-coded to 240 rather than parsed from touchscreen properties.
- Probe logs "no gestures found" for any keycode parse error but continues.

## Test signals
- Test with no keycodes, partial keycodes, all supported gestures, and unsupported gesture IDs.
- Validate reset timing, coordinate masking, active-state release reporting, and IRQ behavior on I2C read errors.
