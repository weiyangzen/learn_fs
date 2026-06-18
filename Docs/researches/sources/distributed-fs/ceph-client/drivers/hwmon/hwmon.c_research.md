# sources/distributed-fs/ceph-client/drivers/hwmon/hwmon.c

## Purpose
`hwmon.c` is the core hwmon class implementation. It creates `/sys/class/hwmon/hwmonN` devices, generates standard sysfs attributes from `hwmon_chip_info`, serializes driver callbacks, bridges eligible temperature channels into thermal zones, supports optional I2C PEC control, emits notifications, and provides devm registration helpers.

## Important APIs, Types, and Functions
`struct hwmon_device` wraps the class device, name/label, chip info, mutex, thermal-zone data, and generated groups. `struct hwmon_device_attribute` records each generated attribute's ops, type, attr, channel index, and formatted name. Registration funnels through `__hwmon_device_register()`, with exported wrappers `hwmon_device_register_with_info()`, `devm_hwmon_device_register_with_info()`, group-based legacy helpers, thermal-only registration, sanitize-name helpers, `hwmon_notify_event()`, `hwmon_lock()`, and `hwmon_unlock()`. Attribute generation uses template arrays per sensor type and `hwmon_genattr()`.

## Control Flow
Class initialization runs early via `subsys_initcall()`, first applying a PCI quirk for an MSI board. Registration allocates an IDA ID, allocates `hwmon_device`, optionally generates attributes from chip channel configs, merges extra groups, copies a firmware `label`, sets class/parent/of_node/driver data, registers the device, and optionally registers thermal zones and I2C PEC support if chip config requests it. Sysfs reads/writes lock the hwmon device mutex and call driver `read`, `read_string`, or `write` callbacks. Unregister releases the device and ID, while devm wrappers attach unregister actions to the parent.

## State and Persistence
The core owns generated attribute memory, the class device, ID allocation, copied labels, and registered thermal-zone tracking for the hwmon device lifetime. It does not cache sensor values; drivers own sensor state. PEC writes mutate the parent I2C client's flags.

## Dependencies and Integration Points
It integrates with the driver core class subsystem, sysfs, IDA, device properties, I2C, thermal OF, PCI quirks, tracepoints, and exported hwmon APIs consumed by nearly every hwmon driver.

## Risks
Because all generated callback access is serialized by a single mutex, slow driver reads can block unrelated attributes. Attribute generation requires visible modes to match available callbacks; driver mistakes fail registration. The `energy64` path casts a `s64` buffer through `long *`, which relies on callback convention and architecture expectations. PEC support assumes a single hwmon child below an I2C client. ID freeing is split between unregister and release paths and depends on correct device names.

## Test Signals
Test registration failure cleanup, generated attribute names and modes for each sensor type, string versus numeric callbacks, extra group merging, label visibility, name sanitization, thermal zone registration and trip writes, event notification names, I2C PEC toggling, devm unregister, and invalid chip-info rejection.
