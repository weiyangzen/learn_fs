# sources/distributed-fs/ceph-client/drivers/iio/humidity/hid-sensor-humidity.c

Purpose: Platform driver that exposes HID sensor hub atmospheric humidity reports as an IIO humidity device with direct raw reads, buffered reports, sample frequency, hysteresis, scale, and offset.

Important APIs/types/functions: `struct hid_humidity_state` stores HID common attributes, humidity attribute metadata, scan buffer, scale components, precision, and value offset. `humidity_parse_report()` discovers report attributes and adapts channel realbits. `humidity_read_raw()` uses HID sensor hub helpers for raw value, scale, offset, sample frequency, and hysteresis. `humidity_write_raw()` updates sample frequency and hysteresis. `humidity_capture_sample()` stores incoming report data, and `humidity_proc_event()` pushes buffered samples when data-ready is set. `hid_humidity_probe()` allocates IIO, parses common attributes, sets up trigger, registers HID callbacks, and registers IIO.

Control flow: probe duplicates the static channel template so scan bits can be adjusted to report size, sets up the HID trigger, registers callbacks for humidity usage, then registers the IIO device. Direct raw reads temporarily power the HID sensor and perform a synchronous input attribute read. Asynchronous HID callbacks capture samples and push timestamped scans after complete report events.

State and persistence: State is per platform device and includes parsed HID report ids/scales and the latest buffered sample. HID common attributes own power, data-ready, sampling frequency, and hysteresis state through common HID sensor code.

Dependencies and integration points: Depends on HID sensor hub, `hid-sensor-trigger.h`, IIO buffers/triggers, platform id `HID-SENSOR-200032`, and namespace `IIO_HID`.

Risks: `humidity_capture_sample()` casts `raw_data` to `s32 *`; report sizes smaller than 32 bits rely on adjusted scan metadata and underlying alignment/packing behavior. Callback struct is static and has its `.pdev` field assigned during probe, so multiple devices may share mutable callback storage. Offset is stored but never explicitly initialized in this file.

Test signals: Test with HID humidity devices/report descriptors of different field sizes, direct raw reads with power state transitions, sample frequency/hysteresis writes, buffered trigger operation, multiple-device registration, and remove cleanup order.
