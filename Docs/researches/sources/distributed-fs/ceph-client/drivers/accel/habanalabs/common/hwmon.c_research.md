# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/hwmon.c

## Purpose
This file exposes firmware-provided HabanaLabs sensors through Linux hwmon. It builds channel metadata from CPUCP sensor descriptors and translates hwmon reads/writes into CPUCP packets.

## Important APIs, Types, And Functions
`hl_build_hwmon_channel_info()` builds dynamic `hwmon_channel_info` arrays. `hl_hwmon_init()`, `hl_hwmon_fini()`, and `hl_hwmon_release_resources()` manage registration and allocated metadata. `hl_read()`, `hl_write()`, and `hl_is_visible()` are the hwmon operations. Sensor helpers get/set temperature, voltage, current, fan, PWM, and power values.

## Control Flow
Channel construction counts sensors by type, allocates config arrays, adjusts flags for firmware/kernel enum compatibility, and stores channel info in `hdev->hl_chip_info->info`. Registration installs `hl_hwmon_ops` and registers with `hwmon_device_register_with_info()`. Reads/writes reject non-operational devices, translate attributes to CPUCP enum values, and call `asic_funcs->send_cpu_message()`.

## State And Persistence
Persistent state is allocated channel metadata, `hdev->hwmon_dev`, and `hdev->hwmon_initialized`. Values are not cached here. Compatibility depends on firmware boot status bits and compile-time hwmon enum layout.

## Dependencies And Integration Points
The file integrates Linux hwmon, PCI/device naming, CPUCP packet definitions, ASIC firmware messaging, and firmware-provided fixed properties.

## Risks
Enum fixup is subtle and can hide sensors or send wrong attributes. Some setter errors are swallowed by `hl_write()`. Metadata allocation spans build/init/release paths and needs exact cleanup.

## Test Signals
Test legacy and mapped CPUCP enums, invalid sensor types, no-sensor devices, sysfs mode bits, read/write during reset, CPUCP errors, registration failure, and release cleanup.
