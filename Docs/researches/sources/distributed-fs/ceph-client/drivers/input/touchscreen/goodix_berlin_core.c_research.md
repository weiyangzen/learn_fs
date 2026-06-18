# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_core.c

## Purpose
`goodix_berlin_core.c` is the shared implementation for newer Goodix Berlin touchscreen ICs. It performs regulator/reset power sequencing, device confirmation, firmware and IC-info discovery, multitouch event parsing, request handling, input device setup, PM, and an admin-only raw register sysfs interface.

## Important APIs, types, and functions
- Packed firmware/version, IC-info, header, touch, and event structures model the Berlin firmware protocol.
- `struct goodix_berlin_core` stores device, regmap, regulators, reset GPIO, touchscreen properties, firmware version, input device, IRQ, runtime `touch_data_addr`, selected IC data, and a reusable event buffer.
- `goodix_berlin_checksum_valid()` verifies u16 additive checksums over firmware, IC-info, headers, and touch data.
- `goodix_berlin_power_on()` enables `vddio`, then `avdd`, deasserts reset, confirms the device by writing/readback of `0xaa` at boot option address, and waits for firmware boot. `goodix_berlin_power_off()` reverses the state.
- `goodix_berlin_read_version()` and `goodix_berlin_get_ic_info()` read and validate firmware metadata, reject dummy all-zero/all-ones bus data, and parse the variable IC-info layout to find `touch_data_addr`.
- `goodix_berlin_irq()` reads the event header plus up to two contacts, validates header checksum, dispatches touch/request events, fetches remaining contacts when needed, and clears the status byte.
- `goodix_berlin_input_dev_config()` configures the MT input device with 10 direct slots and touchscreen properties.
- `registers_read()` and `registers_write()` implement an admin read/write binary sysfs file backed by raw regmap accesses.
- `goodix_berlin_probe()` is exported for bus drivers.

## Control flow
The transport driver initializes a regmap and calls `goodix_berlin_probe()`. Core probe requires a positive IRQ, allocates state, gets optional reset GPIO and required `avdd`/`vddio` regulators, powers the device on, registers a devm power-off action, reads version and IC-info, configures input, requests a threaded IRQ, and finally stores driver data.

The IRQ path performs a fixed first read sized for header plus two contacts and checksum. If the status byte is zero it exits. Otherwise it validates the header, handles touch events by completing the contact buffer and validating the touch checksum, handles reset request events by toggling reset when available, clears the status byte, and returns handled. Suspend disables IRQ and powers down; resume powers on and re-enables IRQ.

## State and persistence
Runtime state is devm-managed and persists for the device lifetime. The only parsed firmware state kept after probe is `touch_data_addr` and `fw_version`. The driver does not update firmware/config; it assumes firmware and config are already programmed. Sysfs register writes can mutate arbitrary device state while powered.

## Dependencies and integration points
The core integrates with regmap, input/MT, touchscreen properties, GPIO descriptors, regulators, device property parsing, sysfs binary attributes, PM helpers, and the I2C/SPI transport wrappers. It exports symbols for loadable transport modules.

## Risks
- IC-info parsing walks a variable-width buffer; offset errors can misinterpret `misc` or read beyond validated layout if structure formats change.
- Raw admin register access is powerful and can conflict with IRQ processing or device firmware state.
- The first IRQ read intentionally over-reads for one contact and under-reads for more than two until a second read; checksum placement is subtle and must match protocol.
- Stylus and gesture events are explicitly unsupported; stylus events are warned once and dropped.
- Suspend/resume fully powers the controller but does not reread IC-info, so firmware state must remain compatible after power cycling.

## Test signals
- Build with both Berlin transports and exercise probe on revision A and D devices.
- Validate bad checksum, dummy data, missing IRQ, missing regulators, invalid touch count, invalid slot ID, and unsupported request code paths.
- IRQ tests should cover 0, 1, 2, and more-than-2 contacts, status clearing, reset request handling, and checksum failures.
- PM tests should confirm regulator/reset ordering and event delivery after resume.
