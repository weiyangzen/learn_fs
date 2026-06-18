# sources/distributed-fs/ceph-client/drivers/iio/adc/rzt2h_adc.c

## Purpose
This platform IIO driver supports the Renesas RZ/T2H and RZ/N2H ADC. It exposes firmware-selected voltage channels with raw reads and a fixed 1.8 V, 12-bit scale.

## Important APIs, types, and functions
`struct rzt2h_adc` contains MMIO base, device pointer, completion, mutex, parsed channels, and channel count. Main routines are `rzt2h_adc_read_single()`, `rzt2h_adc_calibrate()`, `rzt2h_adc_read_raw()`, `rzt2h_adc_parse_properties()`, and the runtime resume callback.

## Control flow
Probe parses channel child nodes through `devm_iio_adc_device_alloc_chaninfo_se()`, maps registers, enables runtime PM with autosuspend, requests the named `adi` IRQ, initializes IIO metadata, and registers the device. A raw read resumes runtime PM, locks the ADC, selects exactly one channel in `ADANSA0`, starts single conversion with interrupt enable, waits for completion for about one microsecond, reads the channel result register, stops conversion, unlocks, and autosuspends.

## State and persistence
The driver has no cached measurement state. It recalibrates on every runtime resume after a required post-module-stop delay. Calibration sets the calibration bit, polls ready, clears calibration, and rejects calibration-error status.

## Dependencies and integration points
It depends on platform MMIO, an IRQ named `adi`, runtime PM, IIO ADC firmware channel helpers, and `renesas,r9a09g077-adc` device-tree binding. There is no regulator or clock handling in this file, so those resources are assumed managed outside or not required by this binding.

## Risks
The conversion wait is based on a sub-microsecond datasheet value rounded to `usecs_to_jiffies(1)`, which may be too coarse or too short depending on scheduling and HZ. `max_channels` is computed during parsing but not used for validation beyond storage, so invalid high channel numbers rely on the helper's range. Frequent autosuspend can trigger repeated calibration cost.

## Test signals
Test valid and invalid firmware channels, raw reads for multiple channels under concurrency, timeout path cleanup, calibration timeout and error handling, IRQ completion, runtime resume recalibration, fixed scale reporting, and autosuspend behavior under repeated reads.
