# sources/distributed-fs/ceph-client/drivers/rtc/rtc-hid-sensor-time.c

Purpose: exposes a HID Sensor Hub time sensor as a read-only RTC. It obtains date/time fields from HID input reports rather than from direct RTC registers.

Important APIs/types/functions: `struct hid_time_state` stores sensor callbacks, common HID attributes, per-field attribute info, buffers, completion, spinlock, and RTC pointer. `hid_time_parse_report()` validates all six time attributes share a report and have acceptable sizes/units. `hid_time_capture_sample()` fills `time_buf`; `hid_time_proc_event()` publishes it to `last_time` and completes waiting readers. `hid_rtc_read_time()` triggers a synchronous report request and waits up to six seconds.

Control flow: probe parses common attributes and the time report, registers callbacks, opens the sensor hub, starts HID I/O early, registers the RTC, and unwinds callback/device state on failure. Reads reinitialize completion, request one raw value to cause the full report to arrive, wait for the event callback, then copy the last completed time under spinlock. Remove closes the hub and unregisters callbacks.

State and persistence: no persistent state is stored by this driver. Runtime state is the latest HID report and synchronization primitives.

Dependencies and integration: depends on HID sensor hub APIs, IIO HID namespace, platform device IDs (`HID-SENSOR-2000a0`), RTC core, completions, and spinlocks.

Risks and test signals: the RTC is read-only and depends on HID report timing. Invalid raw lengths become all-ones values that may later fail RTC validation elsewhere. Test report attribute validation, 8/16/32-bit year handling, timeout and signal interruption, callback ordering, remove while reads are pending, and registration failure unwind.
