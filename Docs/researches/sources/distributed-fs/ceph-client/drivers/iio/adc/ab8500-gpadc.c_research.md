# sources/distributed-fs/ceph-client/drivers/iio/adc/ab8500-gpadc.c

Purpose: built-in IIO GPADC driver for ST-Ericsson AB8500/AB8540 PMICs. It arbitrates software and hardware ADC conversions for battery, charger, accessory, die-temperature, VBAT, VBUS, current, and board-defined channels.

Important APIs/types/functions: `enum ab8500_gpadc_channel` defines hardware and virtual channels. `struct ab8500_gpadc_chan_info` stores per-firmware-channel id, hardware-trigger mode, edge, averaging, and trigger timer. `struct ab8500_gpadc` stores parent device, AB8500 handle, channel table, completion, regulator, IRQs, and calibration data. `ab8500_gpadc_read()` performs conversion sequencing. `ab8500_gpadc_ad_to_voltage()` applies calibrated or interpolated conversion. `ab8500_gpadc_read_calibration_data()` decodes OTP calibration. `ab8500_gpadc_parse_channels()`, `ab8500_gpadc_read_raw()`, PM callbacks, probe, and remove complete the driver.

Control flow: probe parses child firmware nodes into IIO channels, requests software and optional hardware conversion IRQs, gets and enables `vddadc`, enables runtime PM, reads calibration data, registers the IIO device, and leaves the regulator under autosuspend. A read locates the channel, waits for the GPADC not busy, programs averaging and software or hardware trigger registers, enables required buffers/current paths, starts conversion or arms trigger timing, waits for completion IRQ, reads raw data registers, optionally reads a second IBAT conversion, disables GPADC, and releases runtime PM.

State and persistence behavior: calibration gain/offsets are cached for VMAIN, BTEMP, VBAT, and IBAT. Firmware channel definitions persist in devm memory. Runtime PM controls the ADC regulator. Hardware control registers are rewritten for each conversion and disabled afterward.

Dependencies and integration points: depends on AB8500 MFD register access (`abx500_*`), regulator framework, runtime PM, threaded IRQ completions, firmware child nodes, IIO fwnode xlate, and built-in platform-driver registration.

Risks: conversion is not protected by an explicit mutex; it relies on the GPADC busy bit and hardware arbitration, so concurrent consumers can contend. OTP decoding divides by calibration-code deltas without explicit zero checks. Error paths force-disable GPADC and drop PM, but cleanup writes can fail silently. Hardware-triggered double conversions are unsupported. Channel type mapping treats temperatures as voltage-like except current channels.

Test signals: DT child-node parsing and fwnode xlate, missing IRQ/regulator failures, software conversion success and timeout, hardware conversion on AB8500, busy-bit timeout, calibrated and fallback conversion math, IBAT double conversion, runtime PM regulator transitions, and AB8540-specific OTP paths.
