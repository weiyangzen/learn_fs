
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_iio.c

## Purpose
`ssp_iio.c` provides common IIO buffer callbacks and data processing for SSP child sensors. It allocates per-sensor scan buffers, maps buffer enable/disable to SSP MCU sensor enable/disable commands, and pushes MCU-provided samples into IIO buffers with reconstructed timestamps.

## Important APIs, types, and functions
- `ssp_common_buffer_postenable()` allocates `ssp_sensor_data.buffer` sized from `indio_dev->scan_bytes` and enables the sensor with its current SSP delay.
- `ssp_common_buffer_postdisable()` disables the SSP sensor and frees the allocated buffer.
- `ssp_common_process_data()` copies sensor payload bytes into the scan buffer, reads a little-endian 32-bit timestamp delta after the payload, and calls `iio_push_to_buffers_with_timestamp()`.
- All three functions are exported in namespace `IIO_SSP_SENSORS`.

## Control flow
IIO buffer setup for a child sensor calls postenable after scan layout is known. The code looks up the parent `ssp_data` via `indio_dev->dev.parent->parent`, allocates a DMA-capable buffer, then asks the SSP parent to enable the sensor. When the SSP IRQ parser receives bypass data, the child driver's `process_data` wrapper can call `ssp_common_process_data()`, which copies raw channel bytes and appends an absolute timestamp derived from the parent timestamp plus the MCU delta. Postdisable reverses the MCU enable and frees the temporary buffer.

## State and persistence behavior
The only persistent runtime state is `struct ssp_sensor_data::buffer`, allocated while the IIO buffer is enabled. The function relies on parent `ssp_data` for delays and transport. There is no file-backed state.

## Dependencies and integration points
This file depends on the IIO buffer/kfifo infrastructure, `linux/iio/common/ssp_sensors.h` for `struct ssp_sensor_data`, and `ssp_iio_sensor.h` for prototypes and conversion helpers. It integrates with `ssp_dev.c` exported sensor lifecycle calls and with `ssp_spi.c` packet delivery.

## Risks and edge cases
- If `ssp_enable_sensor()` fails in postenable, the allocated buffer is not freed before returning the error, which can leak per-enable memory.
- `ssp_common_process_data()` copies `len` bytes into `spd->buffer` without checking that `len <= indio_dev->scan_bytes`; it depends on caller-provided sensor sizes being correct.
- Timestamp delta is read from `buf + len`; callers must ensure the input frame contains the extra SSP time field.
- Parent lookup assumes a fixed MFD/IIO device hierarchy.

## Test signals
Enable an SSP child buffer and confirm allocation succeeds, the parent MCU receives an enable command, samples appear in the IIO buffer with plausible timestamps, and disable frees state and sends the remove command. Fault injection around enable failure should check for leaked `spd->buffer`.
