
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_iio_sensor.h

## Purpose
`ssp_iio_sensor.h` is a local helper header for SSP IIO child drivers. It defines standard channel macros, a timestamp channel macro, common buffer/data prototypes, and sampling-frequency conversion helpers.

## Important APIs, types, and functions
- `SSP_CHANNEL_AG()` builds signed 16-bit little-endian modified accelerometer/gyroscope-style channel specs with shared sampling-frequency info.
- `SSP_CHAN_TIMESTAMP()` defines the mixed SSP/IIO 64-bit timestamp channel.
- `ssp_common_buffer_postenable()`, `ssp_common_buffer_postdisable()`, and `ssp_common_process_data()` are declared for child drivers.
- `ssp_convert_to_freq()` converts a delay in milliseconds to IIO integer plus micro fractional frequency.
- `ssp_convert_to_time()` converts IIO integer plus micro fractional frequency back to a millisecond delay.

## Control flow
This header has no runtime control flow outside the inline conversion routines. Child drivers include it to define channel arrays and implement read/write sampling-frequency handlers that translate between IIO frequency representation and SSP millisecond delays.

## State and persistence behavior
No state is stored here. Conversion helpers are pure functions over caller-provided values.

## Dependencies and integration points
The macros require IIO channel definitions and bit macros already available to including C files. The prototypes bind to `ssp_iio.c`; the conversion helpers support `ssp_dev.c` delay commands indirectly through child drivers.

## Risks and edge cases
- `ssp_convert_to_freq()` computes `fractional` from the scaled integer frequency before splitting integer and fractional parts; callers should verify the resulting IIO representation for non-divisible millisecond periods.
- `ssp_convert_to_time()` returns zero for a zero frequency, which a caller could pass through as a special/invalid delay unless validated.
- Channel macros are tailored to 16-bit signed LE data; sensors with different sample layouts need custom specs.

## Test signals
Unit-style checks for representative delays and frequencies are useful: 10 ms should map near 100 Hz, 100 ms near 10 Hz, zero should round-trip as zero. Child channel arrays should expose scan types and timestamp layout expected by IIO tools.
