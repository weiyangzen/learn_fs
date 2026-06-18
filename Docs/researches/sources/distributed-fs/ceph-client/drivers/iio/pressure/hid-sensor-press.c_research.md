<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hid-sensor-press.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hid-sensor-press.c

Purpose: IIO driver for HID Sensor Hub atmospheric pressure reports.

Important APIs, types, and functions: `struct press_state` contains HID callbacks, common HID sensor attributes, pressure attribute info, scan buffer, scale fields, offset, and timestamp. `press_parse_report()` discovers report metadata and scale. `press_read_raw()` handles raw pressure, scale, offset, sample frequency, and hysteresis. `press_write_raw()` updates sample frequency and hysteresis. `press_capture_sample()` stores incoming HID samples, and `press_proc_event()` pushes buffered samples.

Control flow: platform probe parses common attributes for HID usage `HID_USAGE_SENSOR_PRESSURE`, duplicates and adjusts channels according to descriptor size, sets up trigger support, registers the IIO device, and registers sensor-hub callbacks. Runtime raw reads power the sensor, request a synchronous raw value, and power it back down. Buffered events are callback-driven by the HID hub.

State and persistence: runtime state includes report metadata, scale/offset, latest sample, and latest timestamp. Sample frequency and hysteresis writes are delegated to HID common helpers and may persist according to hub behavior.

Dependencies and integration points: depends on HID sensor hub, HID IIO common/trigger helpers, platform device ID `HID-SENSOR-200031`, and namespace `IIO_HID`.

Risks: `press_capture_sample()` casts raw HID buffers directly to `u32`/`s64` without length or alignment checks in this file. Timestamp is reused until overwritten, so missing timestamp reports fall back to current IIO time only when zero. Correct scale depends entirely on HID descriptor metadata. Manual unregister/remove paths must stay aligned with non-devm registration.

Test signals: HID descriptor variations for sample size/sign, synchronous raw reads, buffer event ordering with and without timestamp reports, sample-frequency/hysteresis writes, suspend/resume via `hid_sensor_pm_ops`, and callback cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hid-sensor-press.c -->
