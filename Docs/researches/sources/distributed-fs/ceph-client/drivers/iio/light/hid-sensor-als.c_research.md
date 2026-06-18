# sources/distributed-fs/ceph-client/drivers/iio/light/hid-sensor-als.c

## Purpose

`hid-sensor-als.c` is an IIO platform driver for HID sensor hub ambient light usage collections. It exposes any ALS-related HID report fields that are present: intensity, illuminance, color temperature, chromaticity X, and chromaticity Y, plus timestamp. It supports direct raw reads and buffered data pushed from HID callbacks.

## Important APIs, Types, And Functions

`struct als_state` stores HID callbacks, common HID sensor attributes, per-channel HID attribute info, dynamic IIO channel specs, a scan buffer with timestamp, scale and offset metadata, channel count, HID timestamp, and scan mask. `als_read_raw()` reads current values or common attributes. `als_write_raw()` writes sample frequency and hysteresis settings. `als_proc_event()` pushes a complete scan to IIO buffers. `als_capture_sample()` copies HID report fields into the scan buffer. `als_parse_report()` discovers supported usages and adjusts channel bit widths. Probe/remove are `hid_als_probe()` and `hid_als_remove()`.

## Control Flow

Probe retrieves the HID sensor hub device from platform data, parses common attributes, discovers ALS-specific report fields, appends a timestamp channel, installs available scan masks, sets up a HID sensor trigger, registers IIO, and registers HID callbacks. Direct raw reads power the HID sensor on, call `sensor_hub_input_attr_get_raw_value()` for the chosen usage/report ID, and power it off. Buffered capture receives individual samples in `als_capture_sample()` and pushes the assembled scan in `als_proc_event()` when the common `data_ready` flag is set.

## State And Persistence

The dynamic channel list persists for the platform device lifetime and depends on the HID report descriptor. Scale, offset, sample frequency, and hysteresis are represented by HID common attributes rather than local hardware registers. The scan buffer stores the latest captured fields until an event callback pushes them. HID timestamps are converted through `hid_sensor_convert_timestamp()`.

## Dependencies And Integration Points

The driver integrates with HID sensor hub callbacks, `hid-sensor-trigger`, IIO buffer/trigger support, platform IDs `HID-SENSOR-200041` and `HID-SENSOR-LISS-0041`, and `hid_sensor_pm_ops`. It imports the `IIO_HID` namespace.

## Risks And Test Signals

`als_capture_sample()` casts raw data to `u32` or `s64` without checking `raw_len`, relying on HID core guarantees. The same HID illuminance usage feeds both intensity and light channels. Tests should cover report descriptors with each subset of optional channels, signed logical minima, direct reads during power transitions, sample frequency and hysteresis writes, buffer pushes with HID timestamps and fallback timestamps, callback unregister on remove, and scan masks matching discovered channels.
