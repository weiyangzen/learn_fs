# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hynitron_cstxxx.c

## Purpose
`hynitron_cstxxx.c` is an I2C driver for Hynitron CST3xx touchscreens, currently represented by CST340-compatible chip data. It is derived from vendor code without datasheets, validates firmware presence/check code, enters bootloader mode during probe, and reports up to five multitouch contacts.

## Important APIs, types, and functions
- `struct hynitron_ts_chip_data` provides per-chip max touches, firmware check code, and function callbacks for firmware info, bootloader entry, input init, and touch reporting.
- `struct hynitron_ts_data` stores selected chip data, client, input, touchscreen properties, and reset GPIO.
- `hyn_reset_proc()` toggles reset with fixed delays.
- `cst3xx_i2c_write()` retries short raw writes; `cst3xx_i2c_read_register()` reads little-endian 16-bit register addresses.
- `cst3xx_firmware_info()` enters firmware-info mode, validates check code, rejects invalid firmware version, and exits info mode.
- `cst3xx_bootloader_enter()` retries reset plus bootloader command until the bootloader check register returns `0xac`, then resets again.
- `cst3xx_touch_report()` reads and validates the CST3xx touch buffer, sends a finish-read command, parses variable touch layouts, and reports contacts.
- `cst3xx_input_dev_int()` configures the input device, touchscreen properties, defaults, MT slots, and registration.

## Control flow
Probe allocates state, gets OF match data and required reset GPIO, resets, enters bootloader mode, initializes input, verifies firmware info, and requests the threaded IRQ. The IRQ calls the chip-specific report callback. Touch reporting reads the full 28-byte buffer, validates marker bytes, acknowledges completion before parsing, derives touch count, checks the trailing marker for multi-touch reports, parses each 5-byte contact, reports active contacts, and syncs.

## State and persistence
There is no managed firmware update despite bootloader access. Driver state is runtime-only. It verifies firmware presence and chip code during probe but does not store version beyond logs. Hardware reset/bootloader/info commands mutate controller mode transiently.

## Dependencies and integration points
The driver uses I2C raw transfers, GPIO reset, input/MT, touchscreen properties, OF match data, and asynchronous probe preference.

## Risks
- Probe enters bootloader before initializing input and then verifies firmware after input registration; failures can leave a registered input device if devm cleanup is not enough for the exact sequence.
- Protocol constants are inferred from vendor code and comments note missing datasheets, so changes are high-risk.
- Touch count is not clamped before buffer-derived `end_byte`; malformed counts can address beyond meaningful report contents.
- The finger ID sanity check uses `< finger_id`, so an ID equal to `max_touch_num` is not rejected even though slots are zero-based.
- Continuous IRQ behavior while touched can amplify log noise on read/marker failures.

## Test signals
- Probe CST340 hardware through reset, bootloader entry, firmware check-code validation, and invalid firmware version handling.
- Touch tests should cover one, multiple, zero, malformed marker bytes, high touch counts, and boundary finger IDs.
- Regression tests should verify default axis fallback and touchscreen property override behavior.
