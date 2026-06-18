# sources/distributed-fs/ceph-client/drivers/video/backlight/arcxcnn_bl.c

## Purpose
This I2C driver controls ArcticSand ARCxCnnn-family LED backlight controllers, currently matching `arc2c0608`, with 12-bit brightness and configurable LED-string/current behavior.

## Important APIs, types, and functions
`struct arcxcnn_platform_data` captures name, initial brightness, LED enables, fade/config/dimming/filter/trim settings. `struct arcxcnn` stores client, backlight, device, and platform data. Key functions are `arcxcnn_update_field`, `arcxcnn_set_brightness`, `arcxcnn_bl_update_status`, `arcxcnn_backlight_register`, `arcxcnn_parse_dt`, `arcxcnn_probe`, and `arcxcnn_remove`.

## Control flow
Probe checks SMBus byte-data, allocates state, resets the chip, builds platform data from supplied data or defaults plus optional DT properties, clamps initial brightness, writes brightness and configuration registers, sets LED-enable bits, registers a platform backlight, and updates status. Brightness writes split a 12-bit value across LSB/MSB registers. Power state controls standby bit in the command register.

## State and persistence
Runtime state is device-managed. Hardware configuration registers persist until changed or reset. The backlight core stores requested brightness and power state.

## Dependencies and integration points
It depends on I2C SMBus byte operations, optional OF properties (`label`, `default-brightness`, `led-sources`, `arc,*`), and the backlight core.

## Risks and test signals
Risks include unchecked negative SMBus reads when building defaults, no chip-ID verification despite ID registers, DT `led-sources` bit indexing assumptions, ignored return from initial LED enable update, and reset-on-remove side effects. Test signals include DT/default probe paths, invalid LED sources, brightness split at boundaries 0/15/16/4095, power standby toggling, reset failure, and I2C read/write error injection.
