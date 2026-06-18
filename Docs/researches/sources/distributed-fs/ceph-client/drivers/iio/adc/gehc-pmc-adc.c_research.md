# sources/distributed-fs/ceph-client/drivers/iio/adc/gehc-pmc-adc.c

## Purpose
`gehc-pmc-adc.c` is an I2C IIO driver for a GE HealthCare PMC ADC protocol that exposes 16 voltage and 16 current channels. The device returns already-processed signed millivolt or milliampere values.

## Important APIs, types, and functions
- `struct pmc_adc` stores the I2C client.
- `pmc_adc_channels` creates voltage commands `0x10 | channel` and current commands `0x20 | channel`.
- `pmc_adc_read_raw_ch()` uses `i2c_smbus_read_word_swapped()` and sign-extends 16-bit values.
- `pmc_adc_read_raw()` handles `IIO_CHAN_INFO_PROCESSED`.
- `pmc_adc_fwnode_xlate()` maps two-cell firmware references, acquisition type plus channel number, to IIO channel indices.
- Probe enables four regulators, optionally enables an `osc` clock, checks protocol version command `0x01`, and registers the IIO device.

## Control flow
Probe bulk-enables `vdd`, `vdda`, `vddio`, and `vref`, enables optional oscillator clock, allocates the device, reads the protocol version, rejects non-`0x01` protocol, and registers 32 direct-mode channels. Reads perform one SMBus word read using the channel address as command.

## State and persistence
No mutable runtime state is persisted. Regulator and optional clock enablement live for the device lifetime. The protocol version check is probe-time state validation only.

## Dependencies and integration points
The driver integrates with I2C, regulator bulk helpers, optional common clock, IIO direct mode, and firmware IIO consumer mapping using GEHC-specific DT binding constants.

## Risks
- Values are trusted as processed units, so scaling or unit changes in firmware/protocol would break ABI expectations.
- There is no explicit mutex; I2C core serialization is relied on for simple command reads.
- Unsupported protocol versions fail probe, which is correct but requires firmware coordination.

## Test signals
Use an I2C stub or hardware to verify protocol version rejection, signed positive/negative values, all 32 channels, and fwnode references for voltage/current type plus channel number.
