# sources/distributed-fs/ceph-client/drivers/iio/adc/cpcap-adc.c

## Purpose
This Motorola CPCAP PMIC ADC driver exposes 18 IIO channels for battery temperature/voltage, VBUS, die temperature, system/battery currents, USB ID, bank1 auxiliary inputs, and two remuxed channels. It provides raw and processed reads, including calibration, phasing, temperature lookup, and conversion tables derived from older Motorola kernel behavior.

## Important APIs, Types, And Functions
`struct cpcap_adc` holds the PMIC regmap, device, vendor, IRQ, mutex, timing table, waitqueue, and completion flag. Channel behavior is encoded in `bank_phasing[]` and mutable `bank_conversion[]`; per-board timings come from `struct cpcap_adc_ato` match data. `cpcap_adc_calibrate()` and `cpcap_adc_calibrate_one()` populate calibration offsets. `cpcap_adc_setup_bank()`, `cpcap_adc_start_bank()`, and `cpcap_adc_stop_bank()` control conversions. `cpcap_adc_phase()` and `cpcap_adc_convert()` post-process readings. `cpcap_adc_read()` is the IIO callback.

## Control Flow
Probe requires OF match data for timing configuration, initializes state, gets the parent regmap and CPCAP vendor, requests the `adcdone` threaded IRQ, calibrates charge/system current channels, and registers the IIO device. The IRQ thread disables further ADC trigger interrupts, sets `done`, and wakes the waitqueue. For each raw or processed read, the driver initializes a request, locks, starts an immediate conversion with up to five 50 ms retry attempts, reads either the channel register or scaled bank result, restores default ADCC1/ADCC2 state, unlocks, and returns the value. Processed reads apply ST-specific die-temperature math for AD3 or generic phasing/conversion logic for other channels.

## State And Persistence
No files are persisted, but `bank_conversion[]` is global mutable state updated by calibration and by TI vendor reads. This means calibration offsets are shared across device instances, though CPCAP is effectively a singleton PMIC in expected systems. Runtime state includes the waitqueue `done` flag and register setup that is restored after each read. Calibration offsets depend on vendor and measured calibration registers.

## Dependencies And Integration Points
The driver depends on Motorola CPCAP MFD regmap/register definitions, `cpcap_get_vendor()`, platform named IRQ `adcdone`, OF compatibles `motorola,mapphone-cpcap-adc` and `motorola,mot-cpcap-adc`, IIO core, and IIO buffer headers even though no triggered buffer setup is registered. Channels use `IIO_CHAN_INFO_RAW` and `IIO_CHAN_INFO_PROCESSED`.

## Risks And Test Signals
Risks include sparse public documentation, global mutable calibration tables, retry/timeout behavior during ADC start, vendor-specific calibration differences, thermal lookup-table assumptions, and the base compatible without match data returning `-ENODEV`. Test signals include successful calibration offsets for non-TI vendors, TI path using ADCAL registers dynamically, processed battery/current voltage values within table min/max clamps, AD0 thermbias enable delay, timeout after repeated conversion attempts, and default register restoration after failures.
