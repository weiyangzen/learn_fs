# sources/distributed-fs/ceph-client/drivers/iio/adc/sc27xx_adc.c

## Purpose
This platform IIO driver supports Spreadtrum/Unisoc SC27xx PMIC ADC blocks. It exposes 32 voltage channels, raw or processed readings depending on channel, user-writable scale selector, and variant-specific calibration and voltage-ratio conversion.

## Important APIs, types, and functions
`struct sc27xx_adc_data` stores PMIC regmap, base offset, hardware spinlock, mutex, optional VREF regulator, per-channel scale array, and variant data. `struct sc27xx_adc_variant_data` provides module/clock register offsets, scale bit layout, calibration graphs, per-channel scale initialization, ratio callback, and special VREF behavior. Core functions are `sc27xx_adc_read()`, `sc27xx_adc_read_processed()`, `sc27xx_adc_convert_volt()`, `sc27xx_adc_scale_calibration()`, `sc27xx_adc_enable()`, and `sc27xx_adc_probe()`.

## Control flow
Probe obtains the parent PMIC regmap, local `reg` base, IRQ number, hardware spinlock, optional `vref` regulator for variants that need it, initializes default channel scales, enables module and clocks, calibrates big and small scale graphs from nvmem cells, registers cleanup, and registers the IIO device. Reads take a mutex, then `sc27xx_adc_read()` takes the hardware spinlock, optionally raises VREF to 3.5 V for SC2721 channels 30/31, enables ADC, clears IRQ, programs channel and scale, starts a 12-bit one-sample conversion, polls raw IRQ status, reads data, disables ADC, restores VREF, and unlocks. Processed reads convert raw ADC code through calibrated linear graphs and per-channel ratios.

## State and persistence
`channel_scale[]` is mutable through `write_raw()` and persists until driver unload. Calibration mutates the file-scope `big_scale_graph` and `small_scale_graph`, so graph values are shared process-wide after probe. Hardware is enabled for each read but PMIC module clocks remain enabled until devm cleanup.

## Dependencies and integration points
The driver integrates with parent PMIC regmap, nvmem calibration cells `big_scale_calib` and `small_scale_calib`, hardware spinlocks for cross-subsystem arbitration, optional VREF regulator, and compatibles for SC2731, SC2730, SC2721, and SC2720.

## Risks
Calibration cell read errors are not distinguished from valid zero data inside `sc27xx_adc_scale_calibration()`, so missing or failed nvmem may silently alter graph values. Shared global calibration graphs can be problematic if multiple variants probe with different calibration data. `write_raw()` accepts any scale integer and does not validate it against the variant mask. IRQ is fetched but conversions use polling, so interrupt wiring may not be exercised.

## Test signals
Test all compatibles, nvmem present/missing/error cases, processed voltage math for channels 1 and 5 plus ratio-scaled channels, SC2721 VREF switching on channels 30/31, hardware spinlock timeout, scale writes beyond valid range, ADC poll timeout cleanup, and module/clock cleanup on probe failure.
