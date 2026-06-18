# sources/distributed-fs/ceph-client/drivers/iio/light/hid-sensor-prox.c

## Purpose

`hid-sensor-prox.c` is an IIO platform driver for HID human presence, human proximity, and human attention sensors. It exposes discovered HID usages as proximity or attention channels, supports direct raw/processed reads, and pushes buffered samples through HID sensor callbacks.

## Important APIs, Types, And Functions

`struct prox_state` stores HID callbacks, common attributes, per-channel attribute info, channel specs, usage mapping, latest sample array, per-channel scale metadata, scan mask, and channel count. `prox_read_raw()` reads raw/processed values, scale, offset, sample frequency, and hysteresis. `prox_write_raw()` writes sample frequency and hysteresis. `prox_proc_event()` pushes captured data to IIO buffers. `prox_capture_sample()` decodes 1-, 2-, or 4-byte HID sample payloads. `prox_parse_report()` discovers the available HID fields.

## Control Flow

Probe parses common HID attributes, discovers supported proximity/attention usages, builds a compact channel array with scan indexes, sets up a HID trigger, registers the IIO device, and registers sensor hub callbacks. Direct reads power the HID sensor, fetch a raw value from the report ID and usage, multiply human-attention values by 100, and power the sensor off. Buffered samples are stored in `human_presence[]` by usage and pushed when `data_ready` is observed.

## State And Persistence

The channel-to-usage mapping and scale metadata are built once from the HID descriptor. Latest buffered samples live in `human_presence[]`; no local register cache exists. Common attributes hold sample frequency and hysteresis. Offset is always reported as zero.

## Dependencies And Integration Points

The driver depends on HID sensor hub, HID sensor trigger helpers, IIO buffers, platform IDs `HID-SENSOR-200011` and `HID-SENSOR-LISS-0226`, and `hid_sensor_pm_ops`. It imports `IIO_HID`.

## Risks And Test Signals

There is no timestamp channel, so buffer consumers receive only channel samples. `prox_proc_event()` passes `&prox_state->human_presence`, which is an array object pointer; this resolves to the same address but should be kept in mind if refactored. Tests should cover each usage independently, mixed descriptors, attention scaling by 100 in both direct and buffered paths, raw lengths 1/2/4, unsupported raw lengths, sample frequency/hysteresis writes, callback registration failure unwind, and remove cleanup.
