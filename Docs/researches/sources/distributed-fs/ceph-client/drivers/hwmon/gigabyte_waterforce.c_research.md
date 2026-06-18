# sources/distributed-fs/ceph-client/drivers/hwmon/gigabyte_waterforce.c

## Purpose
`gigabyte_waterforce.c` is a HID-backed hwmon driver for Gigabyte AORUS Waterforce X240/X280/X360 USB AIO coolers. It exposes coolant temperature, fan RPM, pump RPM, and read-only PWM duty values through the hwmon class, while leaving HIDRAW enabled so existing user-space tools can still communicate with the device.

## Important APIs, Types, and Functions
The central state is `struct waterforce_data`, which stores the `hid_device`, hwmon/debugfs handles, completions for status and firmware replies, cached sensor values, a shared report buffer, and the `updated` jiffies timestamp. The hwmon surface is described by `waterforce_chip_info`, `waterforce_info`, and `waterforce_hwmon_ops`. `waterforce_is_visible()` exposes only read-only temp, fan, PWM, and label attributes. `waterforce_read()` and `waterforce_read_string()` serve hwmon reads. `waterforce_raw_event()` parses incoming HID reports. `waterforce_write_expanded()` sends zero-padded output reports, while `waterforce_get_status()` and `waterforce_get_fw_ver()` issue commands and wait for completions. `waterforce_debugfs_init()` adds a firmware-version debugfs file when a version was retrieved.

## Control Flow
Probe allocates state, parses and starts HID with `HID_CONNECT_HIDRAW`, opens the device, allocates the maximum-size report buffer, initializes locks and completions, starts I/O, optionally requests firmware version, registers the hwmon device, then creates debugfs. A hwmon read calls `waterforce_get_status()`, which serializes requesters, reuses cached data for two seconds, otherwise reinitializes the status completion under a spinlock, sends `{0x99, 0xDA}`, and waits for `waterforce_raw_event()` to complete it. Raw HID events distinguish firmware reports from status reports by the first two bytes, update cached fields from fixed offsets, complete waiters, and refresh `updated`.

## State and Persistence
State is entirely in-memory and device-local. Sensor readings persist only as cached values until the next successful status report. `firmware_version` is retained for the device lifetime and exposed through debugfs. No nonvolatile device programming is performed.

## Dependencies and Integration Points
The driver integrates with HID, hwmon, debugfs, completions, mutexes, spinlocks, jiffies, and unaligned little-endian helpers. It binds one USB VID/PID pair through `hid_device_id`, uses late init when built in, and manually unregisters hwmon/debugfs/HID resources on remove.

## Risks
The parser trusts report size enough to index fixed offsets; malformed short reports would be dangerous if HID core delivered them. Status requests rely on completion ordering between hwmon readers and hidraw-originated reports, hence the explicit spinlock/reinit sequence. The large 6144-byte report buffer and full-size output report are protocol assumptions. Reads can block for up to two seconds and return timeout errors if firmware does not answer.

## Test Signals
Useful tests are device binding by VID/PID, `sensors` output for temp/fan/pwm attributes, repeated concurrent sysfs reads verifying cache reuse and no stalled completions, debugfs firmware version visibility, timeout behavior with device disconnects, and continued hidraw access by vendor utilities.
