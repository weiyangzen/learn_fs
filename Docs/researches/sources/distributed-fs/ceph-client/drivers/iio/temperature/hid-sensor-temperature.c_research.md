# sources/distributed-fs/ceph-client/drivers/iio/temperature/hid-sensor-temperature.c

Purpose: HID Sensor Hub platform driver that exposes environmental temperature as an IIO temperature device with raw, scale, offset, sampling frequency, hysteresis, trigger, and buffered samples.

Important APIs/types/functions: `struct temperature_state` combines HID common attributes, temperature report metadata, scan buffer, scale fields, and offset. `temperature_read_raw()` handles synchronous raw reads and common HID attributes. `temperature_capture_sample()` stores incoming HID samples; `temperature_proc_event()` pushes buffered data when the trigger marks data ready. Probe parses HID common attributes and report metadata, sets up trigger and callback registration.

Control flow: platform probe allocates IIO state, parses the HID temperature usage, duplicates channel specs so scan bits match descriptor size, computes scale, installs HID trigger, registers callbacks for the temperature usage, and registers IIO. Direct raw reads power the sensor on, fetch a synchronized raw value from the sensor hub, then power it off. Buffered flow captures samples as reports arrive and pushes on send-event callback.

State and persistence: common HID attributes track power/reporting state, sampling frequency, hysteresis, and data-ready atomics. The last captured sample is stored in `scan`. Scale and offset are computed once from report descriptors.

Dependencies/integration: depends on HID sensor hub, HID sensor common IIO helpers, platform devices named `HID-SENSOR-200033`, IIO buffers, and HID trigger support. Imports namespace `IIO_HID`.

Risks and test signals: `raw_data` is cast to `s32 *`, so descriptor size/endianness assumptions should match HID core behavior. Test report sizes, negative logical minimum handling, trigger enable/disable, raw reads around runtime power, callback cleanup on probe failure/remove, and sampling-frequency/hysteresis writes.
