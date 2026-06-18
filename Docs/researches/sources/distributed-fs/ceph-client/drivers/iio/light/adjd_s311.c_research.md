# sources/distributed-fs/ceph-client/drivers/iio/light/adjd_s311.c

## Purpose

`adjd_s311.c` is an I2C IIO driver for the Avago ADJD-S311-CR999 digital color sensor. It exposes 10-bit red, green, blue, and clear intensity channels with per-channel capacitor gain and integration-time controls plus triggered-buffer sampling.

## Important APIs, Types, and Functions

- `struct adjd_s311_data` stores the `i2c_client`.
- `adjd_s311_req_data()` starts a conversion by setting `GSSR`, polls for completion up to ten times with 20 ms sleeps, and returns `-EIO` on timeout.
- `adjd_s311_read_data()` requests fresh data and reads a 10-bit channel word.
- `adjd_s311_read_raw()` handles raw data, hardware gain from `CAP_*`, and integration time from `INT_*`.
- `adjd_s311_write_raw()` programs capacitor gain and integration registers with range validation.
- `adjd_s311_trigger_handler()` collects active scan channels into a four-channel 16-bit buffer.
- `ADJD_S311_CHANNEL()` defines modified RGB/clear IIO intensity channels.

## Control Flow

Probe allocates the IIO device, assigns channel definitions and direct mode, installs a triggered buffer, and registers the device. Every raw data read triggers a new sensor conversion before reading the selected data register. Buffered reads trigger one conversion, iterate only active scan bits, read each selected channel, and push a timestamped sample.

## State and Persistence Behavior

The driver has minimal software state. Hardware registers hold capacitor gain and integration values. There is no mutex around direct reads/writes, so serialization relies on IIO direct/buffer use rules and the I2C bus.

## Dependencies and Integration Points

It depends on I2C SMBus byte/word operations, IIO direct mode, triggered buffers, scan masks from active channels, and module I2C ID matching for `"adjd_s311"`.

## Risks and Edge Cases

The file notes missing calibration, offset mode, and sleep mode. Conversion polling can take about 200 ms before failing. Integration time is returned as a fractional micro value based on measurement rather than formal documentation. Concurrent direct writes while buffered sampling can alter gain or timing mid-stream.

## Test Signals

Test conversion timeout, 10-bit masking, per-channel gain writes outside and inside 0..15, integration writes outside and inside 0..4095, triggered buffers with partial scan masks, and probe/register behavior on SMBus failures.
