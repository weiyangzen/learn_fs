# sources/distributed-fs/ceph-client/drivers/iio/adc/lp8788_adc.c

## Purpose
`lp8788_adc.c` is the IIO ADC child driver for the TI LP8788 MFD. It exposes battery, charger, current, temperature, and auxiliary ADC channels and provides default IIO maps for the LP8788 charger driver.

## Important APIs, types, and functions
- `struct lp8788_adc` stores the parent `struct lp8788`, chosen IIO maps, and a mutex.
- `lp8788_scale` contains per-channel scale values in micro units.
- `lp8788_get_adc_result()` starts conversion for a channel, polls the done register up to five times, reads raw bytes, and assembles a 12-bit result.
- `lp8788_adc_read_raw()` handles raw and scale masks under the mutex.
- `lp8788_iio_map_register()` selects platform-provided maps or default charger maps.

## Control flow
Probe retrieves the parent MFD data, allocates IIO state, registers IIO maps, initializes the mutex, sets direct-mode channel metadata, and registers IIO. Raw reads write the channel/start command, wait 100 to 200 us between done checks, then read and decode the raw result.

## State and persistence
No user-modifiable persistent state exists. Conversion selection and start bits are transient hardware state. Map selection is stored in memory for the device lifetime.

## Dependencies and integration points
The driver depends on LP8788 MFD helpers (`lp8788_write_byte`, `lp8788_read_byte`, `lp8788_read_multi_bytes`), platform data for optional IIO maps, IIO map registration, and direct-mode IIO.

## Risks
- If the done bit never becomes set, the code still reads raw data after retries rather than returning timeout.
- Scale values are fixed table entries and must match the parent PMIC channel definitions.
- Raw read error mapping collapses any `lp8788_get_adc_result()` failure to `-EIO`.

## Test signals
Test all channel scales, raw byte decoding, conversion-done retry behavior including never-done cases, default and platform IIO maps, and parent MFD I/O error propagation.
