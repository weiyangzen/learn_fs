# sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497-core.c

## Purpose
`ltc2497-core.c` provides common IIO logic for LTC2496 SPI and LTC2497/LTC2499 I2C ADC drivers. It owns channel definitions, conversion timing, vref regulator handling, IIO map registration, and exported probe/remove helpers.

## Important APIs, types, and functions
- `ltc2497core_wait_conv()` enforces the 150 ms conversion time and detects when a previous automatic-mode result may still be valid.
- `ltc2497core_read()` performs the two-step conversion model: optionally start a measurement for a new address, wait, then fetch result and start the next conversion.
- `ltc2497core_read_raw()` serializes access and returns raw or regulator-derived scale.
- `ltc2497core_channel` defines 16 single-ended and 16 differential channel specs.
- `ltc2497core_probe()` initializes IIO metadata, primes the device, enables `vref`, registers maps, initializes timing/lock, and registers IIO.
- `ltc2497core_remove()` unregisters IIO, maps, and regulator.

## Control flow
Transport wrappers provide `result_and_measure()`. The core probe sends a default measurement command, enables the reference regulator, registers any platform IIO maps, records default address and timestamp, and registers the direct-mode IIO device. Raw reads lock, call timing logic, maybe prime the requested channel, fetch the completed result, and update `time_prev`.

## State and persistence
The core maintains `addr_prev`, `time_prev`, `ref`, chip resolution/name, mutex, and transport callback. Hardware conversion pipeline state is implicit: each result read also starts a new conversion. No settings persist across detach or power loss.

## Dependencies and integration points
It integrates with IIO direct mode, regulator consumers, platform IIO maps, sleepable conversion delays, exported namespace `LTC2497`, and transport-specific I2C/SPI wrappers.

## Risks
- Conversion timing is central; concurrent access is protected by mutex but interruptible sleeps can return `-ERESTARTSYS`.
- Initial `result_and_measure()` occurs before acquiring/enabling `vref`, which assumes the device can accept setup before reference is enabled or the regulator is already active.
- Common channel addresses must match both SPI and I2C transport command formats.

## Test signals
Test timing paths for fresh, stale, and same-address reads, interrupted sleep, vref scale for 16- and 24-bit variants, IIO map registration failure cleanup, and transport callback error propagation.
