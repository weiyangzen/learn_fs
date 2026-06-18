# sources/distributed-fs/ceph-client/include/linux/hwmon.h

## Purpose
Defines the modern hardware monitoring class interface, sensor types, standard attribute bits, chip/channel descriptors, callback operations, and registration helpers.

## APIs, Control Flow, and State
The header enumerates sensor classes (`chip`, `temp`, `in`, `curr`, `power`, `energy`, `humidity`, `fan`, `pwm`, `intrusion`) and per-class attribute IDs, then maps them to `HWMON_*` bitmasks consumed by channel configs. `struct hwmon_ops` supplies visibility, read, read-string, and write callbacks. `HWMON_CHANNEL_INFO()` builds null-terminated per-channel attribute lists, and `struct hwmon_chip_info` binds those lists to ops. Registration APIs include deprecated group-based registration, preferred `hwmon_device_register_with_info()` and devm variant, thermal registration, unregister, event notification, name sanitization, and hwmon device lock/unlock.

## Dependencies, Integration, Risks, and Tests
Depends on bitops, device core, and optional sysfs attribute groups. Integrates with sysfs hwmon class, thermal zone registration, user-space monitoring tools, and driver-managed private data. State persists in the registered hwmon device, attribute files, driver private data, and class lock. Risks include mismatched config bits and callbacks, bad visibility permissions, invalid names (`-`, `*`, whitespace), missed event notifications, and continuing to use deprecated group APIs. Test signals include sysfs ABI attribute presence/permissions, read/write callback error handling, `hwmon_notify_event()` uevents, name sanitization tests, and lock coverage for concurrent reads/writes.
