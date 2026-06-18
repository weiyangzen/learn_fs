
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_buffer.c

## Purpose
`st_sensors_buffer.c` implements a common triggered-buffer poll handler for ST sensor drivers. It reads active scan channels from regmap-backed data registers and pushes aligned samples with timestamps into IIO buffers.

## Important APIs, types, and functions
- `st_sensors_get_buffer_element()` iterates `indio_dev->active_scan_mask`, aligns the output pointer to each channel's storage size, and performs `regmap_bulk_read()` from channel addresses.
- `st_sensors_trigger_handler()` captures hardware or software timestamp, fills `sdata->buffer_data`, pushes it with `iio_push_to_buffers_with_timestamp()`, and notifies trigger completion.
- `st_sensors_trigger_handler()` is exported in namespace `IIO_ST_SENSORS`.

## Control flow
When a trigger fires, the handler selects `sdata->hw_timestamp` for the device's own hardware trigger, otherwise it uses `iio_get_time_ns()`. It reads every enabled scan channel in order, respecting realbits/shift-derived byte count and storage alignment, then pushes the aggregate buffer and completes the trigger.

## State and persistence behavior
The function uses `struct st_sensor_data::buffer_data` as scratch space and reads `hw_timestamp` when own-trigger mode is active. No durable state is changed.

## Dependencies and integration points
It depends on IIO trigger/buffer APIs, `struct st_sensor_data` from `linux/iio/common/st_sensors.h`, and a configured `regmap` supplied by `st_sensors_i2c.c` or `st_sensors_spi.c`.

## Risks and edge cases
- Buffer sizing relies on `ST_SENSORS_MAX_BUFFER_SIZE` and sensor channel definitions matching actual scan bytes.
- Failed `regmap_bulk_read()` returns `-EIO` without pushing data, but trigger completion still occurs.
- Correct alignment depends on each channel's `storagebits` being valid and nonzero.

## Test signals
Use an ST sensor with buffered capture enabled and verify channel ordering, alignment, endian interpretation, timestamps from hardware trigger vs software trigger, and graceful behavior when a regmap read fails.
