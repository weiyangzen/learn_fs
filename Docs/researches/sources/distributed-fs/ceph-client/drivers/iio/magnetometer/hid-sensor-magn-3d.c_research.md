<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hid-sensor-magn-3d.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hid-sensor-magn-3d.c

Purpose: platform IIO driver that exposes HID Sensor Hub Compass 3D reports as magnetometer and rotation channels. It dynamically maps HID report attributes to IIO channels and buffered samples.

Important APIs/types/functions: `struct magn_3d_state` stores HID callbacks, common HID attributes for magnetic flux and rotation, per-usage attribute info, dynamically allocated IIO value buffer, per-channel value pointers, scale/offset metadata, and timestamp. Key functions are `magn_3d_read_raw()`, `magn_3d_write_raw()`, `magn_3d_proc_event()`, `magn_3d_capture_sample()`, `magn_3d_parse_report()`, `hid_magn_3d_probe()`, and `hid_magn_3d_remove()`.

Control flow: probe parses common HID sensor attributes for usage `HID_USAGE_SENSOR_COMPASS_3D`, clones them for rotation sensitivity handling, scans the report descriptor for supported magnetometer/heading/timestamp usages, allocates an exact channel array and aligned sample buffer, formats scale values, sets up a HID sensor trigger, registers the IIO device, and registers HID callbacks. Raw reads power the HID sensor, synchronously fetch a report value for the selected usage, and power down. Runtime callbacks capture each incoming sample into the per-channel buffer, convert HID timestamps when present, and on report event push a timestamped IIO buffer if data-ready is set.

State/persistence: channel layout and scale/offset metadata are derived from the HID report descriptor at probe and kept in memory. Sample values live in a dynamically allocated buffer; no hardware register state or persistent storage is owned here. Power and sampling/hysteresis configuration is managed through HID sensor common helpers.

Dependencies/integration: depends on HID sensor hub APIs, HID sensor common trigger/PM helpers, IIO direct mode and buffers, platform driver id `HID-SENSOR-200083`, and namespace `IIO_HID`.

Risks: raw sample extraction casts `raw_data` directly to `u32 *`/`s64 *`, so descriptor size/alignment assumptions matter. Channel count includes timestamp handling and value-buffer alignment logic that should be validated for sparse reports. Scale for rotation sensitivity has a separate lookup fallback and may be missing on some descriptors. Only channels present in the HID report are exposed, so userspace must tolerate variable layouts.

Test signals: test with HID devices exposing full and sparse Compass 3D reports, raw reads for each channel type, sample-frequency and hysteresis writes, trigger enable/disable, timestamp conversion, buffer pushes with and without HID timestamps, suspend/resume via `hid_sensor_pm_ops`, and malformed descriptor paths with no supported usages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hid-sensor-magn-3d.c -->
