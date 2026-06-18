# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-trigger.c

Purpose: shared HID Sensor IIO trigger, buffer, FIFO-latency, and power-management helper. It allows concrete HID IIO drivers to set up kfifo buffers, expose hardware FIFO attributes when supported, maintain a trigger for userspace compatibility, and coordinate sensor power/reporting state with runtime PM.

Important APIs, types, and functions: `_hid_sensor_power_state()` opens/closes the HID sensor hub device, sets power/reporting feature values, manages `data_ready`, and waits after enabling based on poll interval. Exported `hid_sensor_power_state()` wraps runtime PM or direct power state. `hid_sensor_setup_trigger()` installs kfifo buffer ops, optional FIFO sysfs attributes, allocates/registers an IIO trigger, sets driver data, initializes delayed power-restoration work, and configures autosuspend. `hid_sensor_remove_trigger()` tears down runtime PM, work, and trigger. Buffer ops call power on/off around buffer enable. `hid_sensor_pm_ops` wires system/runtime suspend and resume.

Control flow: concrete drivers call setup after parsing common attributes. Buffer enable increments requested state and resumes the device; disable drops it. Resume schedules work to restore poll interval, hysteresis, report latency, and requested power state.

State and persistence: state is in caller-owned `struct hid_sensor_common`: trigger pointer, atomics, work item, latency, poll interval, hysteresis, and HID report descriptors. Feature settings are restored after PM transitions.

Dependencies and integration: depends on HID sensor hub, IIO kfifo buffers/triggers, runtime PM, workqueues, and imports `IIO_HID_ATTRIBUTES`.

Risks and test signals: atomic reference handling must avoid double close/open. `hid_sensor_remove_trigger()` unregisters manual trigger resources allocated outside devm. Tests should cover buffer enable/disable races, runtime PM on/off paths, autosuspend restore work, batch-mode FIFO attributes, setup failure unwind, and system suspend/resume.
