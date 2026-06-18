# sources/distributed-fs/ceph-client/drivers/input/touchscreen/imagis.c

## Purpose
`imagis.c` is an I2C driver for Imagis IST30xx/IST3038-family capacitive touch controllers. It uses per-compatible register metadata to validate chip identity, report multitouch contacts and optional touch keys, and power the controller only while the input device is open.

## Important APIs, types, and functions
- `struct imagis_properties` describes interrupt-message register, coordinate register, chip-ID register/value, protocol variant, and touch-key support.
- `struct imagis_ts` stores client, properties, input device, touchscreen properties, two regulators, keycodes, and keycode count.
- `imagis_i2c_read_reg()` sends a big-endian 32-bit register address and reads a 32-bit value with up to three retries.
- `imagis_interrupt()` reads the interrupt message, validates finger count, reads per-finger or shared coordinate registers depending on protocol, reports slots, reports optional keys, and syncs.
- `imagis_power_on()`/`imagis_power_off()` bulk-enable/disable `vdd` and `vddio`.
- `imagis_input_open()`/`imagis_input_close()` start/stop power and IRQ.
- `imagis_init_input_dev()` configures input, keycodes, required touchscreen size properties, and MT slots.
- Per-compatible property tables support IST3032C, IST3038, IST3038B, IST3038C, and IST3038H.

## Control flow
Probe allocates state, gets match data, obtains regulators, powers on long enough to read chip ID, installs devm power-off cleanup, verifies identity, requests an IRQ with `IRQF_NO_AUTOEN`, and registers input. Input open powers the controller and enables IRQ; close disables IRQ and powers off. PM stops/starts only if the input device is enabled.

## State and persistence
The driver has no firmware/config persistence. Keycode mappings and compatible-specific register tables are runtime state. Regulator/IRQ state follows input open/close and PM.

## Dependencies and integration points
It uses I2C, OF match data, regulator bulk APIs, input open/close, input/MT, touchscreen properties, optional `linux,keycodes`, IRQ no-auto-enable, and PM with input-device mutex locking.

## Risks
- Probe powers the controller and installs a devm power-off action before input open; the controller may be powered off after probe while the input device exists, as intended, so IRQ auto-enable must remain disabled.
- For protocol variants without separate per-finger registers, repeated reads of the same coordinate register inside the finger loop rely on device-side sequencing.
- Touchscreen size properties are mandatory; missing DT properties fail probe.
- Touch-key default mappings are only applied for key-capable variants when no property is present.

## Test signals
- Probe each compatible with matching and mismatching chip IDs.
- Input tests should cover protocol A/B coordinate reads, maximum finger count rejection, optional/default keycodes, and required touchscreen-size properties.
- Power tests should verify regulator and IRQ state on input open/close and suspend/resume.
