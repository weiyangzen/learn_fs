# sources/distributed-fs/ceph-client/drivers/iio/adc/intel_dc_ti_adc.c

## Purpose
`intel_dc_ti_adc.c` is an IIO GPADC driver for the Intel Dollar Cove TI PMIC. It exposes battery voltage and PMIC/battery/system temperature channels and registers IIO maps for battery consumers.

## Important APIs, types, and functions
- `struct dc_ti_adc_info` stores mutex, wait queue, parent PMIC regmap, calibration values, and conversion-done flag.
- `dc_ti_adc_channels` defines VBAT, PMICTEMP, BATTEMP, and SYSTEMP0.
- `dc_ti_adc_sample()` enables ADC, selects channel, delays per vendor timing, starts conversion, waits up to 5 seconds, reads 10-bit big-endian result, and disables ADC.
- `dc_ti_adc_raw_to_processed()` applies VBAT zero-scale and gain-error calibration and returns millivolt values.
- `dc_ti_adc_read_raw()` handles scale, raw, processed VBAT, and BATTEMP bias timing.
- Probe reads calibration register, registers default IIO maps, requests threaded IRQ, and registers IIO.

## Control flow
Probe gets the PMIC regmap from the parent MFD, requests the platform IRQ, initializes locking and wait queue, reads VBAT calibration nibbles, registers consumer maps for `chtdc_ti_battery`, and registers direct-mode IIO. Reads serialize on `lock`; battery-temperature reads enable external bias and wait 35 ms before conversion; all conversions are interrupt-notified through `conversion_done`.

## State and persistence
Runtime state includes calibration values and conversion flag. Hardware state includes ADC enable/start, channel select, and external BPTHEM bias. The driver clears start/enable after every sample and does not persist user settings.

## Dependencies and integration points
It integrates with Intel SoC PMIC MFD, regmap, platform IRQ, wait queues, IIO maps, and IIO direct mode.

## Risks
- The 5-second timeout is long for sysfs reads but required by vendor guidance.
- BATTEMP bias clear is attempted after sampling but errors are ignored.
- Processed values exist only for VBAT; callers requesting processed temperature get `-EINVAL` after conversion.
- Timing comments contain microsecond symbols from source comments; exact vendor timing should be preserved.

## Test signals
Test IRQ completion, timeout cleanup, VBAT raw/scale/processed math with signed calibration nibbles, BATTEMP bias enable delay and clear, IIO map consumers, and concurrent reads.
